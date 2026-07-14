#!/usr/bin/env bash
# modal-detect.sh — 5 pattern grep → 平台 (per v2.9 改 schema, 旧名"模态类型"是僵尸 property)
# 用法: bash modal-detect.sh <URL>
# 输出: arXiv / 微信公众号 / 博客 / Twitter / 其他
# v2.9 注: db 实际有两个 select 字段 — `平台` (URL 平台) + `展现形式` (内容形态, 6 选项 [课程/论文/工具/基础知识/博客/帖子])
# 模态类型 是僵尸 property (type=None, options=空), 不要往里写

set -euo pipefail
URL="${1:-}"

case "$URL" in
  *arxiv.org*) echo "arXiv" ;;
  *mp.weixin.qq.com*) echo "微信公众号" ;;
  *bilibili.com*) echo "bilibili" ;;
  *twitter.com*|*x.com*) echo "Twitter" ;;
  *blog*|*medium.com*|*juejin.cn*|*zhuanlan.zhihu.com*|*github.io/posts*|*github.com/blog*) echo "博客" ;;
  *) echo "其他" ;;
esac