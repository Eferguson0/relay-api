from typing import List, Optional

from sqlalchemy.orm import Session

from app.repositories.goal_templates_repository import GoalTemplateRepository
from app.schemas.goal.templates import GoalTemplateRead


class GoalTemplateService:
    """Thin service wrapper so other layers don't instantiate repositories directly."""

    def __init__(self, db: Session):
        self.db = db

    def get_latest_active(self, slug: str) -> Optional[GoalTemplateRead]:
        """Fetch newest active template version for preset building."""
        repo = GoalTemplateRepository(self.db)
        return repo.get_latest_active(slug)


    # Not used yet but will support backfills or debugging once we manage multiple template versions.

    def get(
        self, slug: str, version: Optional[int] = None, active_only: bool = True
    ) -> Optional[GoalTemplateRead]:
        """Retrieve a specific template version (used for backfills or debugging)."""
        repo = GoalTemplateRepository(self.db)
        return repo.get(slug=slug, version=version, active_only=active_only)

    def list_templates(self, active_only: bool = True) -> List[GoalTemplateRead]:
        """Enumerate templates (admin tools, internal audits)."""
        repo = GoalTemplateRepository(self.db)
        return repo.list_templates(active_only=active_only)
