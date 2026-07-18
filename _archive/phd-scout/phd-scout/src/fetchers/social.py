"""L5: Social media fetcher for Xiaohongshu/Zhihu (标注可信度)."""
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SocialFetcher:
    """Fetches information from social platforms (Xiaohongshu, Zhihu)."""

    def __init__(self, timeout: int = 30, retry_times: int = 2):
        self.timeout = timeout
        self.retry_times = retry_times

    async def fetch(self, name: str, affiliation: str) -> dict:
        """
        Fetch information from social platforms.

        L5 is manual annotation mode - output marks `[需手动补充]`.

        Args:
            name: Researcher name
            affiliation: University identifier

        Returns:
            dict with keys: success, name, social_data, source, manual_annotation_needed
        """
        logger.info(f"SocialFetcher: L5 manual mode for {name} @ {affiliation}")

        return {
            "success": False,
            "name": name,
            "affiliation": affiliation,
            "error": "Social media search requires manual annotation",
            "source": "L5_social",
            "manual_annotation_needed": True,
            "proceed_to_l5": False,
            "social_data": {
                "xiaohongshu": [],
                "zhihu": [],
                "weibo": [],
                "bilibili": []
            },
            "confidence": "manual",
            "标注": "[需手动补充]"
        }

    async def search_xiaohongshu(self, name: str, affiliation: str) -> dict:
        """
        Search Xiaohongshu (小红书) for researcher mentions.

        Note: Xiaohongshu has anti-scraping measures. This uses unofficial API
        or marks for manual search.
        """
        return {
            "platform": "xiaohongshu",
            "name": name,
            "affiliation": affiliation,
            "results": [],
            "note": "[需手动补充] 小红书搜索需要人工介入",
            "confidence": 0.0
        }

    async def search_zhihu(self, name: str, affiliation: str) -> dict:
        """
        Search Zhihu for researcher mentions.

        Note: Zhihu has anti-scraping measures. This uses unofficial API
        or marks for manual search.
        """
        return {
            "platform": "zhihu",
            "name": name,
            "affiliation": affiliation,
            "results": [],
            "note": "[需手动补充] 知乎搜索需要人工介入",
            "confidence": 0.0
        }

    async def aggregate_social_data(self, name: str, affiliation: str) -> dict:
        """
        Aggregate data from all social platforms.

        Returns structured data with confidence scores.
        """
        xhs_data = await self.search_xiaohongshu(name, affiliation)
        zhihu_data = await self.search_zhihu(name, affiliation)

        return {
            "name": name,
            "affiliation": affiliation,
            "sources": {
                "xiaohongshu": xhs_data,
                "zhihu": zhihu_data
            },
            "overall_confidence": 0.0,
            "manual_annotation_needed": True,
            "标注": "[需手动补充]"
        }
