# modal-detect.md — 5 pattern 模态判定表 (per Q3 fallback "其他")

| # | Pattern | 模态类型 | URL 示例 | 判定逻辑 (bash case) |
|---|---|---|---|---|
| 1 | arxiv.org | `arXiv` | `https://arxiv.org/abs/1706.03762` | `*arxiv.org*)` |
| 2 | mp.weixin.qq.com | `微信公众号` | `https://mp.weixin.qq.com/s/abc123` | `*mp.weixin.qq.com*)` |
| 3 | Twitter / X | `Twitter` | `https://twitter.com/karpathy/status/1` | `*twitter.com*\|*x.com*)` |
| 4 | 博客 (medium / GitHub blog / 知乎 / 掘金 / GitHub.io) | `博客` | `https://lilianweng.github.io/posts/...` / `https://medium.com/@.../...` / `https://juejin.cn/post/...` | `*blog*\|*medium.com*\|*juejin.cn*\|*zhuanlan.zhihu.com*\|*github.io/posts*\|*github.com/blog*)` |
| 5 | **fallback** | `其他` | bilibili / youtube / 小红书 / github / 其他 | `*)` (Notion schema 已含选项) |

---

## 判定优先级 (order matters)

```bash
case "$URL" in
  *arxiv.org*) echo "arXiv" ;;          # 1️⃣ 优先
  *mp.weixin.qq.com*) echo "微信公众号" ;;  # 2️⃣
  *twitter.com*|*x.com*) echo "Twitter" ;; # 3️⃣
  *blog*|*medium.com*|*juejin.cn*|*zhuanlan.zhihu.com*|*github.io/posts*|*github.com/blog*) echo "博客" ;;  # 4️⃣
  *) echo "其他" ;;                       # 5️⃣ fallback (per Q3)
esac
```

---

## ❓ 边界 case (per Q3 fallback 设计)

| URL | 期望模态 | 实际判定 |
|---|---|---|
| `https://github.com/openai/whisper` (GitHub repo, 不是 blog) | 其他 | ✅ 其他 (没匹配 4 个 blog pattern) |
| `https://github.blog/2024-01-openai-partnership/` (GitHub blog) | 博客 | ✅ 博客 (匹配 *github.com/blog*) |
| `https://www.youtube.com/watch?v=xyz` | 其他 | ✅ 其他 |
| `https://www.bilibili.com/video/BV1xx` | 其他 | ✅ 其他 |
| `https://www.xiaohongshu.com/explore/xyz` | 其他 | ✅ 其他 |
| `https://www.zhihu.com/question/123` (不是 zhuanlan) | 其他 | ✅ 其他 (只有 zhuanlan.zhihu.com 匹配博客) |

---

## ❌ 反模式

| 反模式 | 真因 | 正确做法 |
|---|---|---|
| 写一长串 if-elif 替 case | 维护难, 容易漏 | 用 bash `case ... esac` |
| 判定失败 exit 1 | per Q3 fallback = "其他", 不要 reject user | fallback "其他" 选项 Notion schema 已含 |
| 用 regex 替 shell glob | 复杂度溢出, 性能低 | bash glob 足够 |