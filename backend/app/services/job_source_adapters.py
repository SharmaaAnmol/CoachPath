"""
Permitted Job Data Source Adapters for CoachPath.
Defines provider abstractions, contract models, and implementations for
seed datasets, manual candidate imports, open developer APIs, and mock test sources.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RawJobListing:
    """Standardized unvalidated payload emitted by job source adapters."""
    title: str
    company_name: str
    location: str
    description_text: str
    application_url: str
    source: str
    external_id: Optional[str] = None
    source_url: Optional[str] = None
    remote_type: Optional[str] = None
    employment_type: Optional[str] = "full_time"
    role_id: Optional[str] = None
    experience_level: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    currency: str = "USD"
    posted_at: Optional[datetime] = None
    raw_payload: Optional[Dict[str, Any]] = field(default_factory=dict)


class BaseJobSourceAdapter(abc.ABC):
    """Abstract interface that every job ingestion provider must fulfill."""

    @property
    @abc.abstractmethod
    def source_name(self) -> str:
        """Unique provider identifier ('seed', 'manual', 'arbeitnow', 'mock')."""
        pass

    @property
    @abc.abstractmethod
    def provider_type(self) -> str:
        """Modality ('seed', 'manual', 'api', 'mock')."""
        pass

    @abc.abstractmethod
    async def fetch_jobs(
        self,
        batch_size: int = 50,
        page: int = 1,
        **kwargs: Any,
    ) -> List[RawJobListing]:
        """Fetches a batch of raw job postings from the underlying provider."""
        pass


class SeedJobAdapter(BaseJobSourceAdapter):
    """
    Curated baseline seed job adapter.
    Supplies realistic benchmark tech roles across the 9 canonical CoachPath roles.
    """

    @property
    def source_name(self) -> str:
        return "seed"

    @property
    def provider_type(self) -> str:
        return "seed"

    async def fetch_jobs(
        self,
        batch_size: int = 50,
        page: int = 1,
        **kwargs: Any,
    ) -> List[RawJobListing]:
        from app.db.seeds.job_seed_data import SEED_JOB_DATA

        offset = (page - 1) * batch_size
        slice_items = SEED_JOB_DATA[offset : offset + batch_size]

        results: List[RawJobListing] = []
        for item in slice_items:
            results.append(
                RawJobListing(
                    external_id=item["external_id"],
                    source="seed",
                    source_url=item.get("source_url"),
                    title=item["title"],
                    company_name=item["company_name"],
                    location=item["location"],
                    remote_type=item.get("remote_type", "hybrid"),
                    employment_type=item.get("employment_type", "full_time"),
                    role_id=item.get("role_id"),
                    experience_level=item.get("experience_level", "entry_level"),
                    min_salary=item.get("min_salary"),
                    max_salary=item.get("max_salary"),
                    currency=item.get("currency", "USD"),
                    description_text=item["description_text"],
                    application_url=item["application_url"],
                    posted_at=item.get("posted_at") or datetime.now(timezone.utc),
                    raw_payload=item,
                )
            )
        return results


class ManualImportAdapter(BaseJobSourceAdapter):
    """
    Adapter converting direct user/candidate job submissions into the standard pipeline.
    """

    @property
    def source_name(self) -> str:
        return "manual"

    @property
    def provider_type(self) -> str:
        return "manual"

    async def fetch_jobs(
        self,
        batch_size: int = 50,
        page: int = 1,
        **kwargs: Any,
    ) -> List[RawJobListing]:
        import_request = kwargs.get("import_request")
        if not import_request:
            return []

        raw = RawJobListing(
            external_id=None,
            source="manual",
            source_url=getattr(import_request, "source_url", None),
            title=import_request.title,
            company_name=import_request.company_name,
            location=import_request.location or "Remote",
            remote_type=import_request.remote_type or "remote",
            employment_type="full_time",
            role_id=getattr(import_request, "role_id", None),
            experience_level=getattr(import_request, "experience_level", "entry_level"),
            min_salary=getattr(import_request, "min_salary", None),
            max_salary=getattr(import_request, "max_salary", None),
            currency=getattr(import_request, "currency", "USD"),
            description_text=import_request.description_text,
            application_url=getattr(import_request, "application_url", None)
            or getattr(import_request, "source_url", None)
            or f"https://coachpath.internal/jobs/manual/{import_request.title.lower().replace(' ', '-')}",
            posted_at=datetime.now(timezone.utc),
            raw_payload={
                "title": import_request.title,
                "company_name": import_request.company_name,
                "location": import_request.location,
            },
        )
        return [raw]


class ArbeitnowJobAdapter(BaseJobSourceAdapter):
    """
    Permitted public developer API adapter for Arbeitnow job board.
    Documentation: https://www.arbeitnow.com/api/job-board-api
    """

    BASE_URL = "https://www.arbeitnow.com/api/job-board-api"

    @property
    def source_name(self) -> str:
        return "arbeitnow"

    @property
    def provider_type(self) -> str:
        return "api"

    async def fetch_jobs(
        self,
        batch_size: int = 50,
        page: int = 1,
        **kwargs: Any,
    ) -> List[RawJobListing]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "CoachPath-MarketIntelligence/1.0",
        }
        params = {"page": page}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(self.BASE_URL, headers=headers, params=params)
                if response.status_code != 200:
                    logger.warning(
                        "Arbeitnow API returned HTTP %d: %s",
                        response.status_code,
                        response.text[:200],
                    )
                    return []
                payload = response.json()
        except Exception as exc:
            logger.error("Arbeitnow API request failed: %s", exc)
            return []

        raw_items = payload.get("data", [])
        results: List[RawJobListing] = []

        for item in raw_items[:batch_size]:
            slug = item.get("slug") or str(item.get("created_at"))
            title = item.get("title", "").strip()
            company = item.get("company_name", "").strip()
            location = item.get("location", "Remote").strip()
            is_remote = item.get("remote", False)
            description = item.get("description", "")
            url = item.get("url", f"https://www.arbeitnow.com/view/{slug}")

            remote_type = "remote" if is_remote else ("hybrid" if "hybrid" in description.lower() else "onsite")

            results.append(
                RawJobListing(
                    external_id=slug,
                    source="arbeitnow",
                    source_url=url,
                    title=title,
                    company_name=company,
                    location=location,
                    remote_type=remote_type,
                    employment_type="full_time",
                    role_id=None,  # Classification will infer canonical role
                    experience_level=None,  # Normalizer will infer seniority
                    min_salary=None,
                    max_salary=None,
                    currency="EUR" if "europe" in location.lower() or "germany" in location.lower() else "USD",
                    description_text=description,
                    application_url=url,
                    posted_at=datetime.fromtimestamp(item["created_at"], tz=timezone.utc)
                    if isinstance(item.get("created_at"), (int, float))
                    else datetime.now(timezone.utc),
                    raw_payload=item,
                )
            )

        return results


class MockJobSourceAdapter(BaseJobSourceAdapter):
    """
    Configurable deterministic test adapter for pytest suites and integration harnesses.
    """

    def __init__(self, mock_jobs: Optional[List[RawJobListing]] = None) -> None:
        self._mock_jobs = mock_jobs or []

    def set_jobs(self, jobs: List[RawJobListing]) -> None:
        self._mock_jobs = jobs

    @property
    def source_name(self) -> str:
        return "mock"

    @property
    def provider_type(self) -> str:
        return "mock"

    async def fetch_jobs(
        self,
        batch_size: int = 50,
        page: int = 1,
        **kwargs: Any,
    ) -> List[RawJobListing]:
        offset = (page - 1) * batch_size
        return self._mock_jobs[offset : offset + batch_size]


class JobSourceAdapterFactory:
    """Factory creating and caching job source adapters."""

    _adapters: Dict[str, BaseJobSourceAdapter] = {}

    @classmethod
    def get_adapter(cls, source_name: str) -> BaseJobSourceAdapter:
        source_key = source_name.lower().strip()
        if source_key in cls._adapters:
            return cls._adapters[source_key]

        if source_key == "seed":
            adapter = SeedJobAdapter()
        elif source_key == "manual":
            adapter = ManualImportAdapter()
        elif source_key == "arbeitnow":
            adapter = ArbeitnowJobAdapter()
        elif source_key == "mock":
            adapter = MockJobSourceAdapter()
        else:
            raise ValueError(f"Unknown job source provider: '{source_name}'")

        cls._adapters[source_key] = adapter
        return adapter

    @classmethod
    def register_adapter(cls, source_name: str, adapter: BaseJobSourceAdapter) -> None:
        """Register or override an adapter (useful for injecting mocks in tests)."""
        cls._adapters[source_name.lower().strip()] = adapter

    @classmethod
    def reset(cls) -> None:
        cls._adapters.clear()
