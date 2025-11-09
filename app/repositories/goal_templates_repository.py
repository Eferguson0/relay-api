from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.goal.templates import GoalTemplate
from app.schemas.goal.templates import GoalTemplateRead


class GoalTemplateRepository:
    """Data-access helpers for goal template records."""

    def __init__(self, db: Session):
        self.db = db

    def get_latest_active(self, slug: str) -> Optional[GoalTemplateRead]:
        """Primary entry point: fetch newest active version for variant math."""
        return self.get(slug=slug, version=None, active_only=True)

    # The methods below aren't used yet but will support admin tooling,
    # migrations, and debugging once we manage multiple template versions.

    def _to_schema(self, template: GoalTemplate) -> GoalTemplateRead:
        """Convert ORM row -> schema so callers get validated defaults."""
        return GoalTemplateRead.model_validate(template)

    def get(
        self, slug: str, version: Optional[int] = None, active_only: bool = True
    ) -> Optional[GoalTemplateRead]:
        query = self.db.query(GoalTemplate).filter(GoalTemplate.slug == slug)

        if version is not None:
            query = query.filter(GoalTemplate.version == version)
        else:
            query = query.order_by(GoalTemplate.version.desc())

        if active_only:
            query = query.filter(GoalTemplate.active.is_(True))

        template = query.first()
        return self._to_schema(template) if template else None

    def list_templates(self, active_only: bool = True) -> List[GoalTemplateRead]:
        query = self.db.query(GoalTemplate)
        if active_only:
            query = query.filter(GoalTemplate.active.is_(True))

        rows = (
            query.order_by(
                GoalTemplate.slug.asc(),
                GoalTemplate.version.desc(),
            ).all()
        )
        return [self._to_schema(row) for row in rows]
