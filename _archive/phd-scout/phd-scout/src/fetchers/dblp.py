"""L4: DBLP fetcher for publication data."""
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DBLPFetcher:
    """Fetches publication records from DBLP."""

    BASE_URL = "https://api.dblp.org/v1"

    def __init__(self, timeout: int = 30, retry_times: int = 3):
        self.timeout = timeout
        self.retry_times = retry_times

    async def fetch(self, name: str, affiliation: str) -> dict:
        """
        Fetch publication records from DBLP.

        Args:
            name: Researcher name
            affiliation: University identifier

        Returns:
            dict with keys: success, name, papers, venue_stats, source
        """
        for attempt in range(self.retry_times):
            try:
                result = await self._fetch_publications(name, affiliation)
                if result.get("success"):
                    return result
            except Exception as e:
                logger.warning(f"DBLPFetcher attempt {attempt + 1} failed for {name}: {e}")
                await asyncio.sleep(2 ** attempt)

        logger.warning(f"DBLPFetcher: All attempts failed for {name}, proceeding to L5")
        return {
            "success": False,
            "name": name,
            "affiliation": affiliation,
            "error": "DBLP fetch failed after retries",
            "source": "L4_dblp",
            "proceed_to_l5": True
        }

    async def _fetch_publications(self, name: str, affiliation: str) -> dict:
        """Fetch publications from DBLP."""
        import xml.etree.ElementTree as ET
        import urllib.parse

        try:
            import aiohttp
            has_aiohttp = True
        except ImportError:
            has_aiohttp = False

        query = f"{name} {affiliation}"
        encoded_query = urllib.parse.quote(query)

        url = f"{self.BASE_URL}/search/authors?u={encoded_query}&format=xml"

        try:
            if has_aiohttp:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        if response.status == 429:
                            return {
                                "success": False,
                                "error": "Rate limited (429)",
                                "source": "L4_dblp",
                                "fatal": True,
                                "proceed_to_l5": False
                            }
                        if response.status >= 500:
                            return {
                                "success": False,
                                "error": f"DBLP server error ({response.status})",
                                "source": "L4_dblp",
                                "fatal": True,
                                "proceed_to_l5": False
                            }
                        xml_content = await response.text()
            else:
                import requests
                resp = requests.get(url, timeout=self.timeout)
                if resp.status_code == 429:
                    return {
                        "success": False,
                        "error": "Rate limited (429)",
                        "source": "L4_dblp",
                        "fatal": True,
                        "proceed_to_l5": False
                    }
                xml_content = resp.text

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "L4_dblp",
                "proceed_to_l5": True
            }

        try:
            root = ET.fromstring(xml_content)

            hits = root.findall(".//hit")
            target_author = None
            for hit in hits:
                author_info = hit.find("info")
                if author_info is not None:
                    author_name = author_info.findtext("author", "")
                    if name in author_name or author_name in name:
                        target_author = author_info
                        break

            if target_author is None:
                return {
                    "success": False,
                    "error": "Author not found on DBLP",
                    "source": "L4_dblp",
                    "proceed_to_l5": True
                }

            author_url = target_author.findtext("url", "")
            if not author_url:
                return {
                    "success": False,
                    "error": "No DBLP URL found for author",
                    "source": "L4_dblp",
                    "proceed_to_l5": True
                }

            author_id = author_url.split("/")[-1].replace(".html", "")

            publications_url = f"{self.BASE_URL}/author/{author_id}.xml"

            if has_aiohttp:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        publications_url,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as pub_response:
                        pub_xml = await pub_response.text()
            else:
                pub_resp = requests.get(publications_url, timeout=self.timeout)
                pub_xml = pub_resp.text

            pub_root = ET.fromstring(pub_xml)

            papers = []
            venue_stats = {}

            for article in pub_root.findall(".//article") + pub_root.findall(".//inproceedings"):
                title_elem = article.find("title")
                title = title_elem.text if title_elem is not None else "Unknown"

                year_elem = article.find("year")
                year = int(year_elem.text) if year_elem is not None else None

                venue_elem = article.find("booktitle") or article.find("journal")
                venue = venue_elem.text if venue_elem is not None else None

                if venue:
                    venue_stats[venue] = venue_stats.get(venue, 0) + 1

                paper = {
                    "title": title.strip() if title else "Unknown",
                    "year": year,
                    "venue": venue,
                    "citations": 0
                }
                papers.append(paper)

            return {
                "success": True,
                "name": target_author.findtext("author", name),
                "papers": papers[:50],
                "venue_stats": venue_stats,
                "total_papers": len(papers),
                "source": "L4_dblp"
            }

        except ET.ParseError as e:
            return {
                "success": False,
                "error": f"XML parse error: {e}",
                "source": "L4_dblp",
                "proceed_to_l5": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "L4_dblp",
                "proceed_to_l5": True
            }
