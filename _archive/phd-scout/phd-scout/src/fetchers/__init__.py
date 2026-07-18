"""Fetchers package: L1-L5 data sources for PhD advisor intelligence."""
from .university import UniversityFetcher
from .scholar import ScholarFetcher
from .semantic_scholar import SemanticScholarFetcher
from .dblp import DBLPFetcher
from .social import SocialFetcher

__all__ = [
    "UniversityFetcher",
    "ScholarFetcher",
    "SemanticScholarFetcher",
    "DBLPFetcher",
    "SocialFetcher",
]
