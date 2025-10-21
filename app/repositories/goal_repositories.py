from sqlalchemy.orm import Session

from app.models.goal.general import GoalGeneral
from app.schemas.goal.general import GoalGeneralBulkCreate, GoalGeneralBulkCreateResponse

class GoalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_general_goal(self, user_id: str) -> GoalGeneral:
        return self.db.query(GoalGeneral).filter(GoalGeneral.user_id == user_id).first()

    def create_general_goal(self, goal: GoalGeneral) -> GoalGeneral:
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def update_general_goal(self, goal: GoalGeneral) -> GoalGeneral:
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def delete_general_goal(self, user_id: str) -> GoalGeneral:
        goal = self.db.query(GoalGeneral).filter(GoalGeneral.user_id == user_id).first()
        if not goal:
            return None
        self.db.delete(goal)
        self.db.commit()
        return goal