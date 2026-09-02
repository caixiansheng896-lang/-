# 全网热点实时聚合 🔥

一次命令，聚合 **微博 / 百度 / 知乎 / B站 / 头条 / 抖音** 六大平台的热搜榜单。

所有数据均来自各平台公开接口，无需登录、无需任何 API Key。

## 特性

- 🚀 **并发抓取** —— `ThreadPoolExecutor` 并行拉取全部平台，秒级返回
- 🧩 **插件式数据源** —— 新增平台只需在 `sources.py` 里注册一个函数
- 🛡️ **单平台容错** —— 某个平台挂了不影响其他平台，失败信息单独汇报
- 📄 **多种输出** —— 控制台表格 / Markdown / JSON，可直接写文件
- 🇨🇳 **零依赖登录** —— 只依赖 `requests`，开箱即用

## 安装

```bash
git clone https://github.com/caixiansheng896-lang/-.git
cd -
pip install -r requirements.txt
```

## 使用

```bash
# 抓全部平台，每平台前 10 条，打印到控制台
python -m hotboard

# 只看微博 + 抖音，取前 20 条
python -m hotboard -s weibo,douyin -n 20

# 导出 Markdown 报告
python -m hotboard -f markdown -o today.md

# 导出 JSON（方便程序消费）
python -m hotboard -f json -o hot.json
```

## 输出示例

```text
=== 全网热点聚合 @ 2026-09-03T00:00:00 ===

[微博]
   1. xxxxxx  (12345678)
   2. xxxxxx  (9876543)
...

[百度]
   1. xxxxxx  (876543)
...
```

## 数据源

| 平台 | 接口来源 | 说明 |
| --- | --- | --- |
| 微博 | `weibo.com/ajax/side/hotSearch` | 热搜榜 |
| 百度 | `top.baidu.com/api/board` | 实时热点 |
| 知乎 | `api.zhihu.com/topstory/hot-list` | 热榜 |
| B站 | `api.bilibili.com/x/web-interface/popular` | 热门视频 |
| 头条 | `toutiao.com/hot-event/hot-board` | 热榜 |
| 抖音 | `iesdouyin.com/web/api/v2/hotsearch` | 点热榜 |

> 接口为各平台公开 Web 端接口，仅供学习研究，请勿高频抓取。

## 项目结构

```text
hotboard/
├── hotboard/
│   ├── __init__.py      # 版本信息
│   ├── __main__.py      # CLI 入口
│   ├── core.py          # 并发聚合 / 格式化输出
│   └── sources.py       # 各平台数据源（可扩展）
├── examples/            # 示例输出
├── requirements.txt
├── LICENSE
└── README.md
```

## License

[MIT](LICENSE)
