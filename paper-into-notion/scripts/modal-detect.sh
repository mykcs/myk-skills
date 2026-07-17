#!/usr/bin/env bash
# modal-detect.sh — 6 pattern grep → 平台 (per v4.3 加 papers.cool arxiv 镜像分支)
# 用法: bash modal-detect.sh <URL>
# 输出: arXiv / 微信公众号 / 博客 / Twitter / 其他
# v2.9 注: db 实际有两个 select 字段 — `平台` (URL 平台) + `展现形式` (内容形态, 6 选项 [课程/论文/工具/基础知识/博客/帖子])
# 模态类型 是僵尸 property (type=None, options=空), 不要往里写
# v4.3 注: papers.cool/arxiv/<id> 是 arxiv.org/abs/<id> 的镜像 (paper 卡片美观, 公众号分享常见),
#          必须识别为 arXiv, 否则 fallback "其他" → 标题写 URL + LLM judge 失败, 见 CASE-PAPER-INTO-NOTION-PAPERS-COOL-MIRROR-20260717

set -euo pipefail
URL="${1:-}"

case "$URL" in
  *arxiv.org*|*papers.cool/arxiv*) echo "arXiv" ;;
  *mp.weixin.qq.com*) echo "微信公众号" ;;
  *bilibili.com*) echo "bilibili" ;;
  *twitter.com*|*x.com*) echo "Twitter" ;;
  *blog*|*medium.com*|*juejin.cn*|*zhuanlan.zhihu.com*|*github.io/posts*|*github.com/blog*) echo "博客" ;;
  *) echo "其他" ;;
esac