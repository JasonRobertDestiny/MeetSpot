#!/usr/bin/env python3
"""
为单个 fix commit 生成 postmortem

使用方法:
    python tools/postmortem_generate.py --commit abc1234 [--output postmortem/]

用于 GitHub Actions 中自动为新的 fix commit 生成 postmortem。
"""
import argparse
import asyncio
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

import yaml

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

POSTMORTEM_DIR = Path(__file__).parent.parent / "postmortem"


def is_fix_commit(commit_hash: str) -> bool:
    """检查是否是 fix commit"""
    cwd = POSTMORTEM_DIR.parent
    cmd = ["git", "log", "-1", "--format=%s", commit_hash]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    subject = result.stdout.strip().lower()
    return subject.startswith("fix")


def get_commit_info(commit_hash: str) -> Dict:
    """获取 commit 详细信息"""
    cwd = POSTMORTEM_DIR.parent

    # subject
    cmd = ["git", "log", "-1", "--format=%s", commit_hash]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    subject = result.stdout.strip()

    # body
    cmd = ["git", "log", "-1", "--format=%b", commit_hash]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    body = result.stdout.strip()

    # date
    cmd = ["git", "log", "-1", "--format=%aI", commit_hash]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    date = result.stdout.strip()

    # files changed
    cmd = ["git", "show", commit_hash, "--name-only", "--format="]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    files = [f for f in result.stdout.strip().split("\n") if f]

    # diff (仅 Python 文件)
    cmd = ["git", "show", commit_hash, "-p", "--", "*.py"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    diff = result.stdout[:6000]

    return {
        "hash": commit_hash[:7],
        "full_hash": commit_hash,
        "subject": subject,
        "body": body,
        "date": date,
        "files": files,
        "diff": diff,
    }


def get_next_pm_id(output_dir: Path) -> str:
    """获取下一个 postmortem ID"""
    year = datetime.now().year
    output_dir.mkdir(exist_ok=True)
    existing = list(output_dir.glob(f"PM-{year}-*.yaml"))
    if not existing:
        return f"PM-{year}-001"

    max_num = max(int(f.stem.split("-")[-1]) for f in existing)
    return f"PM-{year}-{max_num + 1:03d}"


def parse_llm_response(response: str) -> Dict:
    """解析 LLM 响应"""
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

    return {"title": "Parse failed", "severity": "low", "tags": ["parse-error"]}


def extract_from_commit(info: Dict) -> Dict:
    """从 commit 消息直接提取（无 LLM fallback）"""
    subject = info.get("subject", "")
    body = info.get("body", "")
    files = info.get("files", [])
    diff = info.get("diff", "")

    # 从 scope 提取 tags
    scope_match = re.search(r"fix\((\w+)\)", subject, re.IGNORECASE)
    tags = [scope_match.group(1)] if scope_match else []

    # 清理标题
    title = subject
    title = re.sub(r"^fix(\([^)]+\))?:\s*", "", title, flags=re.IGNORECASE)

    # 提取函数名
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


async def generate_with_llm(info: Dict) -> Dict:
    """使用 LLM 生成 postmortem"""
    try:
        from app.llm import LLM

        llm = LLM()
    except ImportError as e:
        print(f"Warning: Cannot import LLM module: {e}")
        return extract_from_commit(info)
    except Exception as e:
        print(f"Warning: LLM init failed: {e}")
        return extract_from_commit(info)

    prompt = f"""分析这个 fix commit，生成 postmortem JSON：

Commit: {info['subject']}
Body: {info['body'][:1000]}
Files: {', '.join(info['files'][:10])}
Diff preview: {info['diff'][:2500]}

返回 JSON 格式：
{{
  "title": "简短标题（中文）",
  "description": "问题描述（2-3句话）",
  "root_cause": "根因分析",
  "severity": "medium",
  "triggers": {{
    "files": ["相关文件模式"],
    "functions": ["相关函数名"],
    "patterns": ["正则模式"],
    "keywords": ["关键词"]
  }},
  "fix_pattern": {{
    "approach": "修复方法",
    "key_changes": ["关键变更"]
  }},
  "verification": ["验证点"],
  "tags": ["标签"]
}}

只返回 JSON，不要其他文字。"""

    try:
        response = await llm.ask(
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            temperature=0.2,
        )
        return parse_llm_response(response)
    except Exception as e:
        print(f"Warning: LLM call failed: {e}")
        return extract_from_commit(info)


def save_postmortem(data: Dict, info: Dict, pm_id: str, output_dir: Path) -> Path:
    """保存 postmortem"""
    output_dir.mkdir(exist_ok=True)

    # 确保 triggers 有完整结构
    triggers = data.get("triggers", {})
    if not isinstance(triggers, dict):
        triggers = {}

    pm = {
        "id": pm_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": info["hash"],
        "severity": data.get("severity", "medium"),
        "title": data.get("title", "Untitled"),
        "description": data.get("description", ""),
        "root_cause": data.get("root_cause", ""),
        "triggers": {
            "files": triggers.get("files", info.get("files", [])[:5]),
            "functions": triggers.get("functions", []),
            "patterns": triggers.get("patterns", []),
            "keywords": triggers.get("keywords", []),
        },
        "fix_pattern": data.get("fix_pattern", {}),
        "verification": data.get("verification", []),
        "related": {
            "files_changed": info.get("files", []),
        },
        "tags": data.get("tags", []),
    }

    filepath = output_dir / f"{pm_id}.yaml"
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(pm, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    return filepath


def check_duplicate(info: Dict, output_dir: Path) -> Optional[str]:
    """检查是否已存在相同 commit 的 postmortem"""
    if not output_dir.exists():
        return None

    for f in output_dir.glob("PM-*.yaml"):
        try:
            with open(f, encoding="utf-8") as fp:
                pm = yaml.safe_load(fp)
                if pm and pm.get("source_commit") == info["hash"]:
                    return f.name
        except Exception:
            continue

    return None


async def main():
    parser = argparse.ArgumentParser(description="Generate postmortem for a fix commit")
    parser.add_argument("--commit", required=True, help="Commit hash")
    parser.add_argument("--output", default="postmortem", help="Output directory")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force generation even if not a fix commit",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Skip LLM, use rule-based extraction only",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    if not output_dir.is_absolute():
        output_dir = POSTMORTEM_DIR.parent / args.output

    # 检查是否是 fix commit
    if not args.force and not is_fix_commit(args.commit):
        print(f"Commit {args.commit} is not a fix commit. Skipping.")
        print("Use --force to generate anyway.")
        return

    # 获取 commit 信息
    info = get_commit_info(args.commit)
    print(f"Processing: {info['subject'][:60]}")

    # 检查重复
    existing = check_duplicate(info, output_dir)
    if existing:
        print(f"Postmortem already exists: {existing}")
        return

    # 生成 postmortem
    if args.no_llm:
        data = extract_from_commit(info)
    else:
        data = await generate_with_llm(info)

    # 保存
    pm_id = get_next_pm_id(output_dir)
    filepath = save_postmortem(data, info, pm_id, output_dir)

    print(f"Generated: {filepath}")


if __name__ == "__main__":
    asyncio.run(main())
