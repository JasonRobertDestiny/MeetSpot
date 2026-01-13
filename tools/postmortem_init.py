#!/usr/bin/env python3
"""
Postmortem Onboarding 脚本
分析历史 fix commits，生成初始 postmortem 集合

使用方法:
    python tools/postmortem_init.py [--since 2025-06-01] [--limit 50] [--dry-run]
"""
import argparse
import asyncio
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

POSTMORTEM_DIR = Path(__file__).parent.parent / "postmortem"


def get_fix_commits(since: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """获取 fix commits 列表"""
    cmd = [
        "git",
        "log",
        "--grep=^fix",
        "-i",
        "--all",
        "--format=%H|%s|%aI",
    ]
    if since:
        cmd.extend(["--since", since])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=POSTMORTEM_DIR.parent)
    commits = []

    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|", 2)
        if len(parts) >= 3:
            commits.append(
                {
                    "hash": parts[0],
                    "subject": parts[1],
                    "date": parts[2],
                }
            )

    return commits[:limit]


def get_commit_details(commit_hash: str) -> Dict:
    """获取 commit 的详细信息"""
    cwd = POSTMORTEM_DIR.parent

    # 获取 body
    body_cmd = ["git", "log", "-1", "--format=%b", commit_hash]
    body_result = subprocess.run(body_cmd, capture_output=True, text=True, cwd=cwd)
    body = body_result.stdout.strip()

    # 获取修改的文件
    files_cmd = ["git", "show", commit_hash, "--name-only", "--format="]
    files_result = subprocess.run(files_cmd, capture_output=True, text=True, cwd=cwd)
    files = [f for f in files_result.stdout.strip().split("\n") if f]

    # 获取 diff 内容（限制大小，只看 .py 文件）
    diff_cmd = ["git", "show", commit_hash, "--stat", "-p", "--", "*.py"]
    diff_result = subprocess.run(diff_cmd, capture_output=True, text=True, cwd=cwd)
    diff = diff_result.stdout[:6000]  # 限制 6KB

    return {"body": body, "files": files, "diff": diff}


def assess_commit_quality(commit: Dict, details: Dict) -> float:
    """评估 commit 消息质量，决定是否值得生成 postmortem"""
    score = 0.0
    body = details.get("body", "")
    subject = commit.get("subject", "")

    # 有详细描述
    if len(body) > 50:
        score += 0.3
    if len(body) > 150:
        score += 0.2

    # 有问题描述关键词
    problem_keywords = ["问题", "原因", "修复", "bug", "error", "issue", "cause", "fix"]
    if any(kw in body.lower() for kw in problem_keywords):
        score += 0.2

    # 有结构化格式
    if any(marker in body for marker in ["##", "- ", "1.", "*"]):
        score += 0.1

    # scope 清晰
    if "(" in subject and ")" in subject:
        score += 0.1

    # 修改了重要文件
    important_patterns = ["recommender", "api/index", "llm", "config"]
    if any(
        any(pat in f for pat in important_patterns) for f in details.get("files", [])
    ):
        score += 0.1

    return min(1.0, score)


def parse_llm_response(response: str) -> Dict:
    """健壮的 JSON 解析，处理 LLM 输出的各种格式"""
    # 尝试直接解析
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # 去除 markdown 代码块
    cleaned = re.sub(r"^```(?:json)?\s*", "", response, flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 尝试提取 JSON 对象
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # 返回基础结构
    return {
        "title": "解析失败",
        "description": response[:500],
        "severity": "low",
        "tags": ["parse-failed"],
    }


async def generate_postmortem_with_llm(commit: Dict, details: Dict) -> Dict:
    """使用 LLM 生成 postmortem"""
    try:
        from app.llm import LLM

        llm = LLM()
    except ImportError as e:
        print(f"  Warning: Cannot import LLM module: {e}")
        return extract_from_commit(commit, details)
    except Exception as e:
        print(f"  Warning: LLM init failed: {e}")
        return extract_from_commit(commit, details)

    prompt = f"""分析以下 git fix commit，生成一个 postmortem 条目。

Commit 信息:
- Subject: {commit['subject']}
- Date: {commit['date']}
- Body: {details.get('body', '(无)')[:1000]}

修改的文件:
{chr(10).join(details['files'][:15])}

代码变更摘要:
{details['diff'][:3000]}

请生成 JSON 格式的 postmortem，包含以下字段：
1. title: 简短标题（中文，10-30字）
2. description: 问题描述（2-3句话，描述问题现象和影响）
3. root_cause: 根因分析（1-2句话）
4. severity: critical/high/medium/low（根据影响范围判断）
5. triggers: 对象，包含:
   - files: 相关文件模式列表（如 "app/tool/*.py"）
   - functions: 相关函数名列表（从 diff 中提取）
   - patterns: 正则匹配模式列表（用于匹配未来的 diff 内容）
   - keywords: 关键词列表（中英文都可以）
6. fix_pattern: 对象，包含:
   - approach: 修复方法描述
   - key_changes: 关键变更点列表
7. verification: 验证检查点列表（未来修改相关代码时应检查的事项）
8. tags: 标签列表（用于分类，如 geocoding, ui, api 等）

只返回 JSON，不要其他文字。"""

    try:
        response = await llm.ask(
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            temperature=0.2,
        )
        return parse_llm_response(response)
    except Exception as e:
        print(f"  Warning: LLM call failed: {e}")
        return extract_from_commit(commit, details)


def extract_from_commit(commit: Dict, details: Dict) -> Dict:
    """从 commit 消息直接提取（无 LLM fallback）"""
    subject = commit.get("subject", "")
    body = details.get("body", "")
    files = details.get("files", [])

    # 从 scope 提取 tags
    scope_match = re.search(r"fix\((\w+)\)", subject, re.IGNORECASE)
    tags = [scope_match.group(1)] if scope_match else []

    # 清理标题
    title = subject
    title = re.sub(r"^fix(\([^)]+\))?:\s*", "", title, flags=re.IGNORECASE)

    # 提取函数名
    functions = []
    diff = details.get("diff", "")
    func_matches = re.findall(r"def\s+(\w+)\s*\(", diff)
    functions = list(set(func_matches))[:5]

    return {
        "title": title[:50] if title else "Fix commit",
        "description": body[:300] if body else subject,
        "root_cause": "See commit body for details",
        "severity": "medium",
        "triggers": {
            "files": files[:5],
            "functions": functions,
            "patterns": [],
            "keywords": tags or ["general"],
        },
        "fix_pattern": {
            "approach": title,
            "key_changes": [title],
        },
        "verification": ["Review related code changes"],
        "tags": tags or ["general"],
    }


def get_next_pm_id(year: int) -> str:
    """获取下一个 postmortem ID"""
    POSTMORTEM_DIR.mkdir(exist_ok=True)
    existing = list(POSTMORTEM_DIR.glob(f"PM-{year}-*.yaml"))
    if not existing:
        return f"PM-{year}-001"

    max_num = max(int(f.stem.split("-")[-1]) for f in existing)
    return f"PM-{year}-{max_num + 1:03d}"


def save_postmortem(pm_data: Dict, commit: Dict, details: Dict, pm_id: str) -> Path:
    """保存 postmortem 到 YAML 文件"""
    POSTMORTEM_DIR.mkdir(exist_ok=True)

    # 确保 triggers 有完整结构
    triggers = pm_data.get("triggers", {})
    if not isinstance(triggers, dict):
        triggers = {}

    output = {
        "id": pm_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "source_commit": commit["hash"][:7],
        "severity": pm_data.get("severity", "medium"),
        "title": pm_data.get("title", "Untitled"),
        "description": pm_data.get("description", ""),
        "root_cause": pm_data.get("root_cause", ""),
        "triggers": {
            "files": triggers.get("files", details.get("files", [])[:5]),
            "functions": triggers.get("functions", []),
            "patterns": triggers.get("patterns", []),
            "keywords": triggers.get("keywords", []),
        },
        "fix_pattern": pm_data.get("fix_pattern", {}),
        "verification": pm_data.get("verification", []),
        "related": {
            "files_changed": details.get("files", []),
        },
        "tags": pm_data.get("tags", []),
    }

    filepath = POSTMORTEM_DIR / f"{pm_id}.yaml"
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(
            output, f, allow_unicode=True, default_flow_style=False, sort_keys=False
        )

    return filepath


async def main():
    parser = argparse.ArgumentParser(description="Postmortem Onboarding")
    parser.add_argument("--since", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=50, help="Max commits to process")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no generation")
    parser.add_argument(
        "--min-quality",
        type=float,
        default=0.2,
        help="Minimum quality score to generate postmortem",
    )
    args = parser.parse_args()

    print("Fetching fix commits...")
    commits = get_fix_commits(since=args.since, limit=args.limit)
    print(f"Found {len(commits)} fix commits")

    if not commits:
        print("No fix commits found.")
        return

    generated = 0
    skipped = 0

    for i, commit in enumerate(commits):
        print(f"\n[{i + 1}/{len(commits)}] {commit['hash'][:7]}: {commit['subject'][:60]}")

        details = get_commit_details(commit["hash"])
        quality = assess_commit_quality(commit, details)

        print(f"  Quality: {quality:.2f}, Files: {len(details['files'])}")

        if quality < args.min_quality:
            print(f"  Skipped: quality below threshold ({args.min_quality})")
            skipped += 1
            continue

        if args.dry_run:
            print("  [DRY-RUN] Would generate postmortem")
            continue

        # 生成 postmortem
        pm_data = await generate_postmortem_with_llm(commit, details)

        # 生成 ID（使用 commit 日期的年份）
        year = int(commit["date"][:4])
        pm_id = get_next_pm_id(year)

        filepath = save_postmortem(pm_data, commit, details, pm_id)
        print(f"  Saved: {filepath}")
        generated += 1

    print(f"\n{'=' * 50}")
    print(f"Summary: Generated {generated}, Skipped {skipped}")
    if generated > 0:
        print(f"Postmortems saved to: {POSTMORTEM_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
