"""Keyword-based direction analyzer with Kimi API for borderline cases."""
import json
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class DirectionAnalyzer:
    """
    Analyzes research direction using keyword library + Kimi API for borderline cases.

    Kimi API is called ONLY when paper title/abstract contains ZERO initial keywords.
    """

    KEYWORD_THRESHOLD = 0.7

    def __init__(self, keywords_path: str = "/Users/myk/phd-scout/config/keywords.json"):
        with open(keywords_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        self.primary_keywords = set(k.lower() for k in config.get("primary", []))
        self.secondary_keywords = set(k.lower() for k in config.get("secondary", []))

    def analyze_paper(self, title: str, abstract: Optional[str] = None) -> dict:
        """
        Analyze a single paper's research direction.

        Args:
            title: Paper title
            abstract: Paper abstract (optional)

        Returns:
            dict with keys: is_relevant, confidence, matched_keywords, needs_kimi, reason
        """
        text = f"{title} {abstract or ''}".lower()

        primary_matches = [kw for kw in self.primary_keywords if kw in text]
        secondary_matches = [kw for kw in self.secondary_keywords if kw in text]

        all_matches = primary_matches + secondary_matches

        if not all_matches:
            return {
                "is_relevant": False,
                "confidence": 0.0,
                "matched_keywords": [],
                "needs_kimi": True,
                "reason": "No keywords matched - requires Kimi API review"
            }

        if primary_matches:
            confidence = 1.0
            is_relevant = True
            reason = f"Matched primary keywords: {primary_matches}"
        else:
            confidence = 0.5
            is_relevant = False
            reason = f"Matched only secondary keywords: {secondary_matches}"

        return {
            "is_relevant": is_relevant,
            "confidence": confidence,
            "matched_keywords": all_matches,
            "needs_kimi": False,
            "reason": reason
        }

    async def analyze_with_kimi(self, title: str, abstract: Optional[str] = None) -> dict:
        """
        Use Kimi API to determine if borderline paper is relevant.

        Called ONLY when title/abstract contains ZERO initial keywords.
        """
        if abstract is None:
            return {
                "is_relevant": False,
                "confidence": 0.0,
                "needs_manual_review": True,
                "reason": "No abstract available for Kimi analysis"
            }

        try:
            from openai import OpenAI
        except ImportError:
            logger.warning("OpenAI SDK not installed, using mock Kimi response")
            return await self._mock_kimi_analysis(title, abstract)

        api_key = self._get_kimi_api_key()
        if not api_key:
            logger.warning("Kimi API key not found, using mock analysis")
            return await self._mock_kimi_analysis(title, abstract)

        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.minimax.chat/v1"
            )

            prompt = self._build_kimi_prompt(title, abstract)

            response = await self._call_kimi_async(client, prompt)

            return self._parse_kimi_response(response, title, abstract)

        except Exception as e:
            logger.error(f"Kimi API call failed: {e}")
            return {
                "is_relevant": False,
                "confidence": 0.0,
                "needs_kimi": True,
                "needs_manual_review": True,
                "reason": f"Kimi API failed: {str(e)[:100]}"
            }

    def _get_kimi_api_key(self) -> Optional[str]:
        """Get Kimi API key from environment."""
        import os
        return os.environ.get("KIMI_API_KEY") or os.environ.get("OPENAI_API_KEY")

    def _build_kimi_prompt(self, title: str, abstract: str) -> str:
        """Build prompt for Kimi API."""
        primary_list = ", ".join(self.primary_keywords)
        secondary_list = ", ".join(self.secondary_keywords)

        return f"""You are a research direction classifier for AI/NLP academics.

Given a paper, determine if it is relevant to LLM (Large Language Model) research.

Primary LLM keywords: {primary_list}

Secondary keywords (related but not core LLM): {secondary_list}

Paper Title: {title}

Paper Abstract: {abstract}

Analyze and respond with:
1. Is this paper related to LLM research? (yes/no/maybe)
2. Confidence score (0.0 to 1.0)
3. Brief reasoning

Respond in JSON format:
{{"relevant": "yes|no|maybe", "confidence": 0.0-1.0, "reasoning": "..."}}
"""

    async def _call_kimi_async(self, client, prompt: str) -> str:
        """Make async call to Kimi API."""
        import asyncio

        def _sync_call():
            return client.chat.completions.create(
                model="MiniMax-Text-01",
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _sync_call)
        return response.choices[0].message.content

    def _parse_kimi_response(self, response: str, title: str, abstract: str) -> dict:
        """Parse Kimi API JSON response."""
        try:
            result = json.loads(response)
            relevant = result.get("relevant", "no").lower()
            confidence = float(result.get("confidence", 0.0))

            is_relevant = relevant in ("yes", "maybe")

            return {
                "is_relevant": is_relevant,
                "confidence": confidence,
                "needs_kimi": False,
                "kimi_analysis": True,
                "reason": result.get("reasoning", "")
            }
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse Kimi response: {e}")
            return {
                "is_relevant": False,
                "confidence": 0.0,
                "needs_kimi": True,
                "needs_manual_review": True,
                "reason": f"Kimi response parse failed: {str(e)[:50]}"
            }

    async def _mock_kimi_analysis(self, title: str, abstract: str) -> dict:
        """Mock Kimi analysis when API is unavailable."""
        keywords_in_text = [kw for kw in self.primary_keywords if kw in (title + " " + (abstract or "")).lower()]

        if keywords_in_text:
            return {
                "is_relevant": True,
                "confidence": 0.75,
                "needs_kimi": False,
                "kimi_analysis": True,
                "mock": True,
                "reason": f"Mock analysis: found {keywords_in_text}"
            }

        llm_indicators = ["neural", "network", "deep learning", "transformer", "attention", "language model"]
        found_indicators = [ind for ind in llm_indicators if ind in (title + " " + (abstract or "")).lower()]

        if found_indicators:
            return {
                "is_relevant": True,
                "confidence": 0.5,
                "needs_kimi": False,
                "kimi_analysis": True,
                "mock": True,
                "reason": f"Mock analysis: found indicators {found_indicators}"
            }

        return {
            "is_relevant": False,
            "confidence": 0.0,
            "needs_kimi": False,
            "kimi_analysis": True,
            "mock": True,
            "needs_manual_review": True,
            "reason": "Mock analysis: no LLM indicators found"
        }

    def analyze_papers(self, papers: list) -> dict:
        """
        Analyze a list of papers and compute overall direction score.

        Args:
            papers: List of dicts with 'title' and optional 'abstract'

        Returns:
            dict with keys: direction_score, relevant_papers, total_papers,
                          matched_keywords, needs_kimi_review
        """
        relevant_papers = []
        needs_kimi_review = []
        all_keywords = []

        for paper in papers:
            result = self.analyze_paper(
                paper.get("title", ""),
                paper.get("abstract")
            )

            if result["needs_kimi"]:
                needs_kimi_review.append({
                    "paper": paper,
                    "title": paper.get("title", "")
                })
            elif result["is_relevant"]:
                relevant_papers.append({
                    "paper": paper,
                    "analysis": result
                })
                all_keywords.extend(result["matched_keywords"])

        keyword_count = len(all_keywords)
        total_papers = len(papers)
        direction_score = keyword_count / total_papers if total_papers > 0 else 0.0

        return {
            "direction_score": direction_score,
            "relevant_papers": relevant_papers,
            "total_papers": total_papers,
            "relevant_count": len(relevant_papers),
            "needs_kimi_review": needs_kimi_review,
            "all_matched_keywords": list(set(all_keywords))
        }
