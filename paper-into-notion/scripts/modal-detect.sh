#!/usr/bin/env bash
# modal-detect.sh — 5 pattern grep → 模态类型 (per Q3 fallback "其他")
# 用法: bash modal-detect.sh <URL>
# 输出: arXiv / 微信公众号 / 博客 / Twitter / 其他

set -euo pipefail
URL="${1:-}"

case "$URL" in
  *arxiv.org*) echo "arXiv" ;;
  *mp.weixin.qq.com*) echo "微信公众号" ;;
  *twitter.com*|*x.com*) echo "Twitter" ;;
  *blog*|*medium.com*|*juejin.cn*|*zhuanlan.zhihu.com*|*github.io/posts*|*github.com/blog*) echo "博客" ;;
  *) echo "其他" ;;
esac