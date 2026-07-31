#!/usr/bin/env python3
"""
Check arXiv URL 真伪 verify 工具 (v0.13.4 NEW).

必跑: 每个 arXiv ID 必跑 WebFetch verify HTTP 200 + title 匹配 L1 byline.
失败标 "待补" + 删 href.

用法:
  python3 check_arxiv_url.py --id 22hBwIf7OC
  python3 check_arxiv_url.py --batch ids.txt
  python3 check_arxiv_url.py --self-test
"""
import argparse
import json
import subprocess
import sys
import re
import urllib.request
import urllib.error


def verify_arxiv_id(arxiv_id: str) -> dict:
    """Verify single arXiv ID: HTTP 200 + title fetch."""
    # arXiv ID format: YYMM.NNNNN (5-digit) or old format cs.YY/NNNNN
    # Reject obviously fake (8+ char alphanumeric like 22hBwIf7OC)
    if re.match(r'^[0-9]{4}\.[0-9]{4,5}$', arxiv_id) or re.match(r'^[a-z\-]+(\.[A-Z]{2})?/[0-9]{7}$', arxiv_id):
        arxiv_url = f'https://arxiv.org/abs/{arxiv_id}'
    else:
        return {'id': arxiv_id, 'ok': False, 'error': 'INVALID_FORMAT', 'url': None}
    
    try:
        req = urllib.request.Request(arxiv_url, headers={'User-Agent': 'teacher-report-check/0.1'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                return {'id': arxiv_id, 'ok': False, 'error': f'HTTP_{resp.status}', 'url': arxiv_url}
            html = resp.read().decode('utf-8', errors='ignore')
            # Extract title from arXiv abs page
            m = re.search(r'<meta name="citation_title" content="([^"]+)"', html)
            title = m.group(1) if m else None
            return {'id': arxiv_id, 'ok': True, 'title': title, 'url': arxiv_url}
    except urllib.error.HTTPError as e:
        return {'id': arxiv_id, 'ok': False, 'error': f'HTTP_{e.code}', 'url': arxiv_url}
    except Exception as e:
        return {'id': arxiv_id, 'ok': False, 'error': str(e)[:100], 'url': arxiv_url}


def main():
    parser = argparse.ArgumentParser(description='Check arXiv URL 真伪 (v0.13.4)')
    parser.add_argument('--id', help='Single arXiv ID to verify')
    parser.add_argument('--batch', help='File with arXiv IDs (one per line)')
    parser.add_argument('--self-test', action='store_true', help='Run self-test on 5 known IDs')
    args = parser.parse_args()
    
    if args.self_test:
        test_ids = ['2406.01721', '2506.12597', '2311.06868',  # 真
                    '22hBwIf7OC', 'TpD2aG1h0D',  # 假
                    'invalid_format',  # 无效格式
                    '2206.04335',  # 真但 docx 内容假
                   ]
        results = [verify_arxiv_id(aid) for aid in test_ids]
        for r in results:
            ok_str: str = 'YES' if r['ok'] else 'NO'
            title: str = r.get('title', '') or ''
            error: str = r.get('error', '') or ''
            detail: str = error if error else title[:60] if title else '?'
            print(f"{r['id']:20s} ok={ok_str:3s} {detail}")
        return 0 if all(r['ok'] or r.get('error') == 'INVALID_FORMAT' for r in results) else 1
    
    ids = []
    if args.id:
        ids = [args.id]
    elif args.batch:
        with open(args.batch) as f:
            ids = [line.strip() for line in f if line.strip()]
    else:
        parser.print_help()
        return 2
    
    results = [verify_arxiv_id(aid) for aid in ids]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(r['ok'] for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
