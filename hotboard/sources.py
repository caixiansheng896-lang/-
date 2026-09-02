"""各平台热搜数据源定义。

每个数据源实现 fetch() -> list[HotItem]，HotItem 定义在 models 中。
所有数据源都只依赖公开接口，无需登录态。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, List

import requests

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
TIMEOUT = 10


@dataclass
class HotItem:
    """统一的榜单条目。"""

    source: str      # 平台名，如 "微博"
    rank: int        # 名次
    title: str       # 标题
    url: str         # 详情链接
    score: int = 0   # 热度值（各平台口径不同，仅作参考）


def _strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html).strip()


def fetch_weibo() -> List[HotItem]:
    """微博热搜榜（需要带 Referer 头，否则 403）。"""
    resp = requests.get(
        "https://weibo.com/ajax/side/hotSearch",
        headers={
            "User-Agent": UA,
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://weibo.com/hot/search",
        },
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()["data"]["realtime"][:50]
    items = []
    for i, entry in enumerate(data, 1):
        word = entry.get("note") or entry.get("word", "")
        items.append(
            HotItem(
                source="微博",
                rank=i,
                title=word,
                url=f"https://s.weibo.com/weibo?q=%23{word}%23",
                score=int(entry.get("num", 0)),
            )
        )
    return items


def fetch_baidu() -> List[HotItem]:
    """百度热搜榜（接口返回双层嵌套，需要展开）。"""
    resp = requests.get(
        "https://top.baidu.com/api/board?platform=wise&tab=realtime",
        headers={"User-Agent": UA},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    entries = []
    for card in resp.json()["data"]["cards"]:
        for wrapper in card.get("content", []):
            # wrapper 可能直接是条目（含 word），也可能再包一层 content
            if "word" in wrapper:
                entries.append(wrapper)
            for inner in wrapper.get("content", []):
                if "word" in inner:
                    entries.append(inner)
    items = []
    for i, entry in enumerate(entries[:50], 1):
        items.append(
            HotItem(
                source="百度",
                rank=i,
                title=_strip_tags(entry.get("word", "")),
                url=entry.get("url", ""),
                score=int(entry.get("hotScore", 0)),
            )
        )
    return items


def fetch_zhihu() -> List[HotItem]:
    """知乎热榜。"""
    resp = requests.get(
        "https://api.zhihu.com/topstory/hot-list?limit=50",
        headers={"User-Agent": UA},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    items = []
    for i, entry in enumerate(resp.json()["data"], 1):
        target = entry["target"]
        items.append(
            HotItem(
                source="知乎",
                rank=i,
                title=target.get("title", ""),
                url=f"https://www.zhihu.com/question/{target.get('id', '')}",
                score=int(entry.get("detail_text", "0").split(" ")[0].replace("万热度", "0000").replace(",", "")) if entry.get("detail_text") else 0,
            )
        )
    return items


def fetch_bilibili() -> List[HotItem]:
    """B站热门视频。"""
    resp = requests.get(
        "https://api.bilibili.com/x/web-interface/popular?ps=50",
        headers={"User-Agent": UA, "Referer": "https://www.bilibili.com"},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    items = []
    for i, entry in enumerate(resp.json()["data"]["list"], 1):
        items.append(
            HotItem(
                source="B站",
                rank=i,
                title=entry.get("title", ""),
                url=f"https://www.bilibili.com/video/{entry.get('bvid', '')}",
                score=int(entry.get("stat", {}).get("view", 0)),
            )
        )
    return items


def fetch_toutiao() -> List[HotItem]:
    """今日头条热榜。"""
    resp = requests.get(
        "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc",
        headers={"User-Agent": UA},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    items = []
    for i, entry in enumerate(resp.json()["data"], 1):
        items.append(
            HotItem(
                source="头条",
                rank=i,
                title=entry.get("Title", ""),
                url=entry.get("Url", ""),
                score=int(entry.get("HotValue", 0)),
            )
        )
    return items


def fetch_douyin() -> List[HotItem]:
    """抖音热点榜。"""
    resp = requests.get(
        "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/",
        headers={"User-Agent": UA},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    items = []
    for i, entry in enumerate(resp.json()["word_list"], 1):
        items.append(
            HotItem(
                source="抖音",
                rank=i,
                title=entry.get("word", ""),
                url="https://www.douyin.com/hot/" + entry.get("sentence_id", ""),
                score=int(entry.get("hot_value", 0)),
            )
        )
    return items


# 数据源注册表：新增平台只需在这里注册
SOURCES: dict[str, Callable[[], List[HotItem]]] = {
    "weibo": fetch_weibo,
    "baidu": fetch_baidu,
    "zhihu": fetch_zhihu,
    "bilibili": fetch_bilibili,
    "toutiao": fetch_toutiao,
    "douyin": fetch_douyin,
}

SOURCE_NAMES = {
    "weibo": "微博",
    "baidu": "百度",
    "zhihu": "知乎",
    "bilibili": "B站",
    "toutiao": "头条",
    "douyin": "抖音",
}
