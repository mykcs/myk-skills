"""L3: Semantic Scholar API fetcher."""
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SemanticScholarFetcher:
    """Fetches paper and author data from Semantic Scholar API."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, retry_times: int = 3):
        self.api_key = api_key
        self.timeout = timeout
        self.retry_times = retry_times

    async def fetch(self, name: str, affiliation: str) -> dict:
        """
        Fetch author and paper data from Semantic Scholar.

        Args:
            name: Researcher name
            affiliation: University identifier

        Returns:
            dict with keys: success, name, papers, hindex_estimate, source
        """
        for attempt in range(self.retry_times):
            try:
                result = await self._fetch_author_data(name, affiliation)
                if result.get("success"):
                    return result
            except Exception as e:
                logger.warning(f"SemanticScholarFetcher attempt {attempt + 1} failed for {name}: {e}")
                await asyncio.sleep(2 ** attempt)

        logger.error(f"SemanticScholarFetcher: All attempts failed for {name}, proceeding to L4")
        return {
            "success": False,
            "name": name,
            "affiliation": affiliation,
            "error": "Semantic Scholar fetch failed after retries",
            "source": "L3_semantic_scholar",
            "proceed_to_l4": True
        }

    async def _fetch_author_data(self, name: str, affiliation: str) -> dict:
        """Fetch author data from Semantic Scholar Graph API."""
        import aiohttp

        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        author_url = f"{self.BASE_URL}/author/search"
        params = {
            "query": f"{name} {affiliation}",
            "limit": 10,
            "fields": "authorId,name,affiliation,hIndex,citationCount,paperCount"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    author_url,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 429:
                        return {
                            "success": False,
                            "error": "Rate limited (429)",
                            "source": "L3_semantic_scholar",
                            "fatal": True,
                            "proceed_to_l4": False
                        }
                    if response.status == 500:
                        return {
                            "success": False,
                            "error": "Semantic Scholar server error (500)",
                            "source": "L3_semantic_scholar",
                            "fatal": True,
                            "proceed_to_l4": False
                        }
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "source": "L3_semantic_scholar",
                            "proceed_to_l4": True
                        }

                    data = await response.json()

        except ImportError:
            logger.warning("aiohttp not installed, using sync fallback")
            import requests
            resp = requests.get(author_url, params=params, headers=headers, timeout=self.timeout)
            data = resp.json()

        authors = data.get("data", [])
        target_author = None
        for author in authors:
            if name in author.get("name", ""):
                target_author = author
                break

        if not target_author:
            return {
                "success": False,
                "error": "Author not found on Semantic Scholar",
                "source": "L3_semantic_scholar",
                "proceed_to_l4": True
            }

        author_id = target_author.get("authorId")

        papers_url = f"{self.BASE_URL}/author/{author_id}/papers"
        paper_params = {
            "limit": 50,
            "fields": "title,year,citationCount,abstract,venue"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    papers_url,
                    params=paper_params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as paper_response:
                    papers_data = await paper_response.json()
        except ImportError:
            resp = requests.get(papers_url, params=paper_params, headers=headers, timeout=self.timeout)
            papers_data = resp.json()

        papers = []
        for paper in papers_data.get("data", []):
            papers.append({
                "title": paper.get("title", "Unknown"),
                "year": paper.get("year"),
                "citations": paper.get("citationCount", 0),
                "abstract": (paper.get("abstract") or "")[:500],
                "venue": paper.get("venue")
            })

        return {
            "success": True,
            "name": target_author.get("name"),
            "affiliation": target_author.get("affiliation"),
            "hindex": target_author.get("hIndex"),
            "citedby": target_author.get("citationCount"),
            "paper_count": target_author.get("paperCount"),
            "papers": papers,
            "source": "L3_semantic_scholar"
        }
