"""核心聚合逻辑：并发抓取各平台榜单并合并。"""

from __future__ import annotations

import datetime
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

from .sources import SOURCES, SOURCE_NAMES, HotItem


def fetch_all(sources: Optional[List[str]] = None, top: int = 10) -> dict:
    """并发抓取指定平台，返回 {平台: [HotItem]}。

    单个平台失败不影响其他平台，失败平台记录在 errors 中。
    """
    keys = sources or list(SOURCES.keys())
    results: dict[str, List[HotItem]] = {}
    errors: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=len(keys) or 1) as pool:
        futures = {pool.submit(SOURCES[k]): k for k in keys if k in SOURCES}
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as exc:  # noqa: BLE001 - 单平台容错
                errors[key] = f"{type(exc).__name__}: {exc}"

    payload = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "boards": {
            SOURCE_NAMES[k]: [item_to_dict(i) for i in items[:top]]
            for k, items in results.items()
        },
    }
    if errors:
        payload["errors"] = {SOURCE_NAMES.get(k, k): v for k, v in errors.items()}
    return payload


def item_to_dict(item: HotItem) -> dict:
    return {
        "rank": item.rank,
        "title": item.title,
        "url": item.url,
        "score": item.score,
    }


def to_markdown(payload: dict) -> str:
    """把聚合结果渲染为 Markdown。"""
    lines = [f"# 全网热点聚合（{payload['generated_at']}）", ""]
    for board, items in payload["boards"].items():
        lines.append(f"## {board}")
        lines.append("")
        lines.append("| 排名 | 热点 | 热度 |")
        lines.append("| ---: | --- | ---: |")
        for it in items:
            title = it["title"].replace("|", "\\|")
            lines.append(f"| {it['rank']} | [{title}]({it['url']}) | {it['score']} |")
        lines.append("")
    if payload.get("errors"):
        lines.append("> 以下平台抓取失败：" + "、".join(payload["errors"]))
        lines.append("")
    return "\n".join(lines)


def to_console(payload: dict) -> str:
    """渲染为控制台文本。"""
    lines = [f"=== 全网热点聚合 @ {payload['generated_at']} ===", ""]
    for board, items in payload["boards"].items():
        lines.append(f"[{board}]")
        for it in items:
            lines.append(f"  {it['rank']:>2}. {it['title']}  ({it['score']})")
        lines.append("")
    if payload.get("errors"):
        lines.append("抓取失败: " + "; ".join(f"{k} - {v}" for k, v in payload["errors"].items()))
    return "\n".join(lines)


def to_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
