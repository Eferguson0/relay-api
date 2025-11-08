from sqlalchemy.orm import Session

from app.models.goal.general import GoalGeneral
from app.models.goal.macros import GoalMacros

# TODO: Reconcile transaction boundaries (commit/rollback) between services and repositories.
class GoalRepository:
    def __init__(self, db: Session):
        self.db = db

# General Goal Repository

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

# Macro Goal Repository

    def get_macro_goal(self, user_id: str) -> GoalMacros:
        return self.db.query(GoalMacros).filter(GoalMacros.user_id == user_id).first()

    def create_macro_goal(self, goal: GoalMacros) -> GoalMacros:
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def update_macro_goal(self, goal: GoalMacros) -> GoalMacros:
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def delete_macro_goal(self, user_id: str) -> GoalMacros:
        goal = self.db.query(GoalMacros).filter(GoalMacros.user_id == user_id).first()
        if not goal:
            return None
        self.db.delete(goal)
        self.db.commit()
        return goal