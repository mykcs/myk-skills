"""L2: Google Scholar fetcher using scholarly library with proxy rotation."""
import asyncio
import logging
from typing import Optional
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)


@dataclass
class ScholarProfile:
    name: str
    affiliation: str
    hindex: Optional[int]
    hindex5y: Optional[int]
    i10index: Optional[int]
    i10index5y: Optional[int]
    citedby: int
    papers: list


class ScholarFetcher:
    """Fetches Google Scholar profile using scholarly library."""

    PROXY_POOL = [
        "http://proxy1:port",
        "http://proxy2:port",
        "http://proxy3:port",
    ]

    def __init__(self, timeout: int = 30, retry_times: int = 3):
        self.timeout = timeout
        self.retry_times = retry_times
        self.current_proxy = None

    def _rotate_proxy(self) -> Optional[str]:
        """Rotate to next proxy from pool."""
        if not self.PROXY_POOL:
            return None
        self.current_proxy = random.choice(self.PROXY_POOL)
        return self.current_proxy

    async def fetch(self, name: str, affiliation: str) -> dict:
        """
        Fetch Google Scholar profile for a researcher.

        Args:
            name: Researcher name
            affiliation: University/college identifier

        Returns:
            dict with keys: success, name, hindex, hindex5y, i10index, i10index5y,
                          citedby, papers, source
        """
        for attempt in range(self.retry_times):
            try:
                result = await self._fetch_scholarly(name, affiliation)
                if result.get("success"):
                    return result
            except Exception as e:
                logger.warning(f"ScholarFetcher attempt {attempt + 1} failed for {name}: {e}")
                await asyncio.sleep(2 ** attempt)

        logger.error(f"ScholarFetcher: All attempts failed for {name}, proceeding to L3")
        return {
            "success": False,
            "name": name,
            "affiliation": affiliation,
            "error": "Google Scholar fetch failed after retries",
            "source": "L2_scholar",
            "proceed_to_l3": True
        }

    async def _fetch_scholarly(self, name: str, affiliation: str) -> dict:
        """Use scholarly library to fetch Google Scholar data."""
        try:
            from scholarly import scholarly
        except ImportError:
            logger.warning("scholarly not installed, L2 will fail")
            return {
                "success": False,
                "error": "scholarly library not available",
                "source": "L2_scholar",
                "proceed_to_l3": True
            }

        proxy = self._rotate_proxy()

        search_query = f"{name} {affiliation}"

        try:
            search_results = await asyncio.to_thread(scholarly.search_author, search_query)

            author = None
            for result in search_results:
                if name in result.get("name", ""):
                    author = result
                    break

            if not author:
                return {
                    "success": False,
                    "error": "Author not found on Google Scholar",
                    "source": "L2_scholar",
                    "proceed_to_l3": True
                }

            filled_author = await asyncio.to_thread(scholarly.fill, author)

            papers = []
            for pub in filled_author.get("publications", [])[:20]:
                paper_info = {
                    "title": pub.get("bib", {}).get("title", "Unknown"),
                    "year": pub.get("bib", {}).get("pub_year"),
                    "citations": pub.get("num_citations", 0),
                    "abstract": pub.get("bib", {}).get("abstract", "")[:500] if pub.get("bib", {}).get("abstract") else None,
                }
                papers.append(paper_info)

            return {
                "success": True,
                "name": filled_author.get("name"),
                "affiliation": filled_author.get("affiliation"),
                "hindex": filled_author.get("hindex"),
                "hindex5y": filled_author.get("hindex5y"),
                "i10index": filled_author.get("i10index"),
                "i10index5y": filled_author.get("i10index5y"),
                "citedby": filled_author.get("citedby"),
                "papers": papers,
                "source": "L2_scholar"
            }

        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate limit" in error_str:
                return {
                    "success": False,
                    "error": "Rate limited (429)",
                    "source": "L2_scholar",
                    "fatal": True,
                    "proceed_to_l3": False
                }
            if "500" in error_str or "service unavailable" in error_str:
                return {
                    "success": False,
                    "error": "Google Scholar service error (500)",
                    "source": "L2_scholar",
                    "fatal": True,
                    "proceed_to_l3": False
                }
            if "auth" in error_str or "unauthorized" in error_str:
                return {
                    "success": False,
                    "error": "Authentication failed",
                    "source": "L2_scholar",
                    "fatal": True,
                    "proceed_to_l3": False
                }
            return {
                "success": False,
                "error": str(e),
                "source": "L2_scholar",
                "proceed_to_l3": True
            }
