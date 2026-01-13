#!/usr/bin/env python3
"""
Postmortem 匹配检查脚本
检查当前变更是否触发历史 postmortem

使用方法:
    python tools/postmortem_check.py [--base main] [--mode warn|block]

返回码:
    0 - 无匹配或仅警告
    1 - 发现高置信度匹配（blocking mode）
    2 - 错误
"""
import argparse
import fnmatch
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

POSTMORTEM_DIR = Path(__file__).parent.parent / "postmortem"


@dataclass
class MatchResult:
    """单个匹配结果"""

    pm_id: str
    reason: str
    confidence: float


@dataclass
class AggregatedMatch:
    """聚合后的匹配结果"""

    pm_id: str
    reasons: List[str] = field(default_factory=list)
    max_confidence: float = 0.0
    match_count: int = 0
    final_confidence: float = 0.0
    has_file_match: bool = False
    has_content_match: bool = False


class PostmortemMatcher:
    """Postmortem 匹配器"""

    # 匹配权重
    WEIGHT_FILE_EXACT = 0.8
    WEIGHT_FILE_PATTERN = 0.6
    WEIGHT_FUNCTION = 0.7
    WEIGHT_PATTERN = 0.5
    WEIGHT_KEYWORD = 0.4

    def __init__(self):
        self.postmortems = self._load_all_postmortems()

    def _load_all_postmortems(self) -> List[Dict]:
        """加载所有 postmortem 文件"""
        pms = []
        if not POSTMORTEM_DIR.exists():
            return pms

        for f in POSTMORTEM_DIR.glob("PM-*.yaml"):
            try:
                with open(f, encoding="utf-8") as fp:
                    pm = yaml.safe_load(fp)
                    if pm:
                        pms.append(pm)
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}", file=sys.stderr)

        return pms

    def match_files(self, changed_files: List[str]) -> List[MatchResult]:
        """匹配修改的文件"""
        matches = []

        for pm in self.postmortems:
            triggers = pm.get("triggers", {})
            pm_files = triggers.get("files", [])
            pm_id = pm.get("id", "unknown")

            for changed in changed_files:
                for pattern in pm_files:
                    if self._file_matches(changed, pattern):
                        # 精确匹配 vs 模式匹配
                        is_exact = "*" not in pattern and "?" not in pattern
                        confidence = (
                            self.WEIGHT_FILE_EXACT if is_exact else self.WEIGHT_FILE_PATTERN
                        )
                        matches.append(
                            MatchResult(
                                pm_id=pm_id,
                                reason=f"File: {changed} ~ {pattern}",
                                confidence=confidence,
                            )
                        )

        return matches

    def match_diff_content(self, diff: str) -> List[MatchResult]:
        """匹配 diff 内容中的函数名和模式"""
        matches = []

        for pm in self.postmortems:
            triggers = pm.get("triggers", {})
            pm_id = pm.get("id", "unknown")

            # 函数名匹配
            for func in triggers.get("functions", []):
                if not func:
                    continue
                try:
                    if re.search(rf"\b{re.escape(func)}\b", diff):
                        matches.append(
                            MatchResult(
                                pm_id=pm_id,
                                reason=f"Function: {func}",
                                confidence=self.WEIGHT_FUNCTION,
                            )
                        )
                except re.error:
                    continue

            # 正则模式匹配
            for pattern in triggers.get("patterns", []):
                if not pattern:
                    continue
                try:
                    if re.search(pattern, diff, re.IGNORECASE):
                        matches.append(
                            MatchResult(
                                pm_id=pm_id,
                                reason=f"Pattern: {pattern}",
                                confidence=self.WEIGHT_PATTERN,
                            )
                        )
                except re.error:
                    continue

            # 关键词匹配
            for keyword in triggers.get("keywords", []):
                if not keyword:
                    continue
                if keyword.lower() in diff.lower():
                    matches.append(
                        MatchResult(
                            pm_id=pm_id,
                            reason=f"Keyword: {keyword}",
                            confidence=self.WEIGHT_KEYWORD,
                        )
                    )

        return matches

    def _file_matches(self, filepath: str, pattern: str) -> bool:
        """检查文件路径是否匹配模式"""
        # 支持 glob 模式
        if fnmatch.fnmatch(filepath, pattern):
            return True
        # 也尝试匹配文件名部分
        if fnmatch.fnmatch(Path(filepath).name, pattern):
            return True
        # 检查是否包含（用于简单的路径匹配）
        if "*" not in pattern and "?" not in pattern:
            return pattern in filepath
        return False

    def aggregate_matches(
        self, file_matches: List[MatchResult], content_matches: List[MatchResult]
    ) -> Dict[str, AggregatedMatch]:
        """聚合匹配结果，计算综合置信度"""
        result: Dict[str, AggregatedMatch] = {}

        all_matches = file_matches + content_matches
        for match in all_matches:
            if match.pm_id not in result:
                result[match.pm_id] = AggregatedMatch(pm_id=match.pm_id)

            agg = result[match.pm_id]
            agg.reasons.append(match.reason)
            agg.max_confidence = max(agg.max_confidence, match.confidence)
            agg.match_count += 1

            if "File" in match.reason:
                agg.has_file_match = True
            if "Function" in match.reason or "Pattern" in match.reason:
                agg.has_content_match = True

        # 计算综合置信度
        for pm_id, agg in result.items():
            base = agg.max_confidence
            # 每增加一个匹配项，加 0.1 bonus（最多 0.3）
            count_bonus = min(0.3, 0.1 * (agg.match_count - 1))
            # 如果同时有文件匹配和内容匹配，额外加 0.1
            cross_bonus = 0.1 if (agg.has_file_match and agg.has_content_match) else 0
            agg.final_confidence = min(1.0, base + count_bonus + cross_bonus)

        return result

    def get_postmortem_details(self, pm_id: str) -> Optional[Dict]:
        """获取 postmortem 详情"""
        for pm in self.postmortems:
            if pm.get("id") == pm_id:
                return pm
        return None


def get_changed_files(base_ref: str) -> List[str]:
    """获取相对于 base 的变更文件"""
    cwd = POSTMORTEM_DIR.parent

    # 尝试不同的 diff 方式
    # 1. 三点 diff（用于 PR）
    cmd = ["git", "diff", "--name-only", f"{base_ref}...HEAD"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

    if result.returncode != 0:
        # 2. 两点 diff
        cmd = ["git", "diff", "--name-only", f"{base_ref}..HEAD"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

    if result.returncode != 0:
        # 3. 直接对比
        cmd = ["git", "diff", "--name-only", base_ref]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

    return [f for f in result.stdout.strip().split("\n") if f]


def get_diff_content(base_ref: str) -> str:
    """获取相对于 base 的 diff 内容"""
    cwd = POSTMORTEM_DIR.parent

    # 只看代码文件的 diff
    extensions = ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx"]
    cmd = ["git", "diff", f"{base_ref}...HEAD", "--"] + extensions
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

    if result.returncode != 0:
        cmd = ["git", "diff", f"{base_ref}..HEAD", "--"] + extensions
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

    if result.returncode != 0:
        cmd = ["git", "diff", base_ref, "--"] + extensions
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

    return result.stdout


def main():
    parser = argparse.ArgumentParser(description="Postmortem Check")
    parser.add_argument("--base", default="main", help="Base branch/commit")
    parser.add_argument(
        "--mode",
        choices=["warn", "block"],
        default="warn",
        help="warn: only print, block: exit 1 on high confidence",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Confidence threshold for blocking (default: 0.7)",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    args = parser.parse_args()

    if not POSTMORTEM_DIR.exists():
        print("No postmortem directory found. Run postmortem_init.py first.")
        sys.exit(0)

    matcher = PostmortemMatcher()

    if not matcher.postmortems:
        print("No postmortems found.")
        sys.exit(0)

    # 获取变更
    changed_files = get_changed_files(args.base)
    diff_content = get_diff_content(args.base)

    if not changed_files:
        print("No changes detected.")
        sys.exit(0)

    print(f"Checking {len(changed_files)} changed files against {len(matcher.postmortems)} postmortems...")

    # 执行匹配
    file_matches = matcher.match_files(changed_files)
    content_matches = matcher.match_diff_content(diff_content)

    # 聚合结果
    results = matcher.aggregate_matches(file_matches, content_matches)

    if not results:
        print("No postmortem matches found.")
        sys.exit(0)

    # 输出结果
    blocking = []
    warnings = []

    sorted_results = sorted(
        results.items(), key=lambda x: x[1].final_confidence, reverse=True
    )

    for pm_id, agg in sorted_results:
        confidence = agg.final_confidence
        is_blocking = confidence >= args.threshold
        level = "BLOCK" if is_blocking else "WARN"

        # 获取 postmortem 详情
        pm = matcher.get_postmortem_details(pm_id)
        if not pm:
            pm = {"title": "Unknown", "severity": "unknown"}

        print(f"\n[{level}] {pm_id} ({confidence:.0%} confidence)")
        print(f"  Title: {pm.get('title', 'N/A')}")
        print(f"  Severity: {pm.get('severity', 'N/A')}")
        print(f"  Reasons:")
        for reason in agg.reasons[:5]:  # 最多显示5个原因
            print(f"    - {reason}")

        if pm.get("verification"):
            print(f"  Verification checklist:")
            for check in pm["verification"]:
                print(f"    [ ] {check}")

        if is_blocking:
            blocking.append(pm_id)
        else:
            warnings.append(pm_id)

    # 总结
    print(f"\n{'=' * 50}")
    print(f"Summary: {len(blocking)} blocking, {len(warnings)} warnings")

    # 决定退出码
    if blocking and args.mode == "block":
        print(f"\n{len(blocking)} postmortem(s) triggered with high confidence.")
        print("Please review the changes and verify they don't reintroduce past issues.")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
