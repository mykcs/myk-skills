"""L1: University/College official website fetcher using Playwright."""
import asyncio
import re
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FacultyMember:
    name: str
    title: str
    affiliation: str
    page_url: Optional[str]
    research_interests: Optional[str]
    email: Optional[str]
    profile_image: Optional[str]


class UniversityFetcher:
    """Fetches faculty information from university/college official websites."""

    def __init__(self, timeout: int = 30, retry_times: int = 3):
        self.timeout = timeout
        self.retry_times = retry_times
        self.browser = None

    async def _init_browser(self):
        """Initialize Playwright browser."""
        try:
            from playwright.async_api import async_playwright
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
        except ImportError:
            logger.warning("Playwright not installed, falling back to HTTP-only mode")
            self.browser = None

    async def _close_browser(self):
        """Close Playwright browser."""
        if self.browser:
            await self.browser.close()

    async def fetch(self, name: str, affiliation: str) -> dict:
        """
        Fetch faculty information from university website.

        Args:
            name: Faculty member name
            affiliation: University/college identifier (e.g., "tsinghua", "pku")

        Returns:
            dict with keys: success, name, affiliation, title, interests, email,
                          profile_url, page_url, source
        """
        if not self.browser:
            await self._init_browser()

        for attempt in range(self.retry_times):
            try:
                result = await self._fetch_with_browser(name, affiliation)
                if result.get("success"):
                    return result
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {name} @ {affiliation}: {e}")
                await asyncio.sleep(2 ** attempt)

        return {
            "success": False,
            "name": name,
            "affiliation": affiliation,
            "error": f"All {self.retry_times} attempts failed",
            "source": "L1_university"
        }

    async def _fetch_with_browser(self, name: str, affiliation: str) -> dict:
        """Use Playwright to fetch faculty page."""
        try:
            from playwright.async_api import TimeoutError as PlaywrightTimeout
        except ImportError:
            return {"success": False, "error": "Playwright not available", "source": "L1_university"}

        import json
        from pathlib import Path
        skill_dir = Path(__file__).resolve().parent.parent.parent
        univ_path = skill_dir / "config" / "universities.json"
        with open(univ_path, "r", encoding="utf-8") as f:
            universities_config = json.load(f)

        if affiliation not in universities_config:
            return {"success": False, "error": f"Unknown affiliation: {affiliation}", "source": "L1_university"}

        school_urls = universities_config[affiliation]

        for school_name, url in school_urls.items():
            try:
                page = await self.browser.new_page()
                await page.goto(url, timeout=self.timeout * 1000, wait_until="networkidle")

                content = await page.content()

                faculty_data = await self._parse_faculty_list(content, name, school_name)

                if faculty_data:
                    await page.close()
                    return faculty_data

                await page.close()
            except Exception as e:
                logger.debug(f"Failed to fetch {school_name} from {url}: {e}")
                continue

        return {"success": False, "error": "Faculty not found on any school page", "source": "L1_university"}

    async def _parse_faculty_list(self, content: str, name: str, school: str) -> dict:
        """Parse faculty information from page HTML content."""
        name_patterns = [
            rf'<a[^>]*href=[^>]*>[^{"<"}*{re.escape(name)}][^<]*</a>',
            rf'class="name"[^>]*>{re.escape(name)}</div>',
            rf'class="title"[^>]*>[^<]*{re.escape(name)}[^<]*</div>',
        ]

        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        title_patterns = [
            r'(教授|副教授|助理教授|讲师|院士|长江学者|杰青)',
            r'(Professor|Associate Professor|Assistant Professor)',
        ]

        email_match = re.search(email_pattern, content)
        email = email_match.group(1) if email_match else None

        combined_interests = []
        interests_pattern = r'(研究方向|研究兴趣|Research Interest)[：:]\s*([^\n<>]+)'
        interests_matches = re.findall(interests_pattern, content)
        for _, interest in interests_matches:
            cleaned = interest.strip()
            if cleaned:
                combined_interests.append(cleaned)

        research_interests = "; ".join(combined_interests) if combined_interests else None

        title = None
        for pattern in title_patterns:
            title_match = re.search(pattern, content)
            if title_match:
                title = title_match.group(0)
                break

        return {
            "success": True,
            "name": name,
            "affiliation": school,
            "title": title,
            "interests": research_interests,
            "email": email,
            "profile_url": None,
            "page_url": None,
            "source": "L1_university"
        }
