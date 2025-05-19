import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, sessionmaker, joinedload, selectinload
from sqlalchemy import func, desc, or_
from datetime import datetime

# Corrected imports for models:
from ..models.enhanced_models import Goal, GoalCheckIn, GoalStatus, Habit # Models from enhanced_models
from ..models.category import Category # Category from its own file
from ..models.value import Value # Value from its own file

logger = logging.getLogger(__name__)

class GoalService:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    def create_goal(self, name: str, description: str, target_date: datetime,
                   status: GoalStatus,
                   parent_id: Optional[int] = None,
                   linked_value_ids: Optional[List[int]] = None,
                   linked_habit_ids: Optional[List[int]] = None) -> Goal:
        with self.Session() as session:
            goal = Goal(
                name=name,
                description=description,
                target_date=target_date,
                parent_id=parent_id,
                status=status
            )
            
            if linked_value_ids:
                values = session.query(Value).filter(Value.id.in_(linked_value_ids)).all()
                goal.values.extend(values)
            
            if linked_habit_ids:
                habits = session.query(Habit).filter(Habit.id.in_(linked_habit_ids)).all()
                goal.supporting_habits.extend(habits)
                
            session.add(goal)
            session.commit()
            session.refresh(goal)
            return goal

    def update_goal(self, goal_id: int, name: str, description: str, target_date: datetime,
                    status: GoalStatus,
                    parent_id: Optional[int] = None,
                    linked_value_ids: Optional[List[int]] = None,
                    linked_habit_ids: Optional[List[int]] = None) -> Optional[Goal]:
        with self.Session() as session:
            goal = session.query(Goal).options(
                joinedload(Goal.values),
                joinedload(Goal.supporting_habits)
            ).filter(Goal.id == goal_id).first()
            
            if goal:
                goal.name = name
                goal.description = description
                goal.target_date = target_date
                goal.status = status
                goal.parent_id = parent_id

                goal.values.clear()
                if linked_value_ids:
                    values = session.query(Value).filter(Value.id.in_(linked_value_ids)).all()
                    goal.values.extend(values)
                
                goal.supporting_habits.clear()
                if linked_habit_ids:
                    habits = session.query(Habit).filter(Habit.id.in_(linked_habit_ids)).all()
                    goal.supporting_habits.extend(habits)

                session.commit()
                session.refresh(goal)
            return goal

    def get_goal(self, goal_id: int) -> Optional[Goal]:
        with self.Session() as session:
            return session.query(Goal).filter(Goal.id == goal_id).first()

    def get_sub_goals(self, parent_id: int) -> List[Goal]:
        with self.Session() as session:
            return session.query(Goal).filter(Goal.parent_id == parent_id).all()

    def get_all_goals_for_parent_selection(self) -> List[Goal]:
        """Fetches all goals, typically for populating a parent selection dropdown."""
        with self.Session() as session:
            # For simplicity, initially load all. Could be optimized later if needed.
            # Could also add options to eager load parent_id or necessary fields for display.
            return session.query(Goal.id, Goal.name, Goal.parent_id).order_by(Goal.name).all()

    def update_goal_status(self, goal_id: int, status: GoalStatus) -> Optional[Goal]:
        with self.Session() as session:
            goal = session.query(Goal).filter(Goal.id == goal_id).first()
            if goal:
                goal.status = status
                session.commit()
                session.refresh(goal)
            return goal

    def create_check_in(self, goal_id: int, reflection: str,
                       progress_percentage: float, notes: Optional[str] = None, 
                       contributing_habit_ids: Optional[List[int]] = None,
                       check_in_date: Optional[datetime] = None) -> GoalCheckIn:
        with self.Session() as session:
            goal = session.query(Goal).filter(Goal.id == goal_id).first()
            if not goal:
                raise ValueError(f"Goal with id {goal_id} not found.")
                
            final_check_in_date = check_in_date if check_in_date is not None else datetime.utcnow()

            check_in = GoalCheckIn(
                goal_id=goal_id,
                reflection=reflection,
                progress_percentage=progress_percentage,
                notes=notes,
                check_in_date=final_check_in_date
            )
            
            if contributing_habit_ids:
                contributing_habits = session.query(Habit).filter(Habit.id.in_(contributing_habit_ids)).all()
                check_in.contributing_habits.extend(contributing_habits)
            
            session.add(check_in)
            session.commit()
            session.refresh(check_in)
            return check_in

    def get_check_ins(self, goal_id: int, start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> List[GoalCheckIn]:
        with self.Session() as session:
            query = session.query(GoalCheckIn).filter(GoalCheckIn.goal_id == goal_id)
            if start_date:
                query = query.filter(GoalCheckIn.check_in_date >= start_date)
            if end_date:
                query = query.filter(GoalCheckIn.check_in_date <= end_date)
            return query.order_by(GoalCheckIn.check_in_date.desc()).all()

    def get_goals_by_target_date(self, target_date: datetime.date) -> List[Goal]:
        """Get goals that have a specific target_date (ignoring time)."""
        with self.Session() as session:
            return session.query(Goal).filter(func.date(Goal.target_date) == target_date).all()

    def get_check_ins_for_date_with_goal(self, check_in_date: datetime.date) -> List[GoalCheckIn]:
        """Get check-ins for a specific date, eager loading the associated goal."""
        with self.Session() as session:
            return session.query(GoalCheckIn).options(
                joinedload(GoalCheckIn.goal)
            ).filter(func.date(GoalCheckIn.check_in_date) == check_in_date).all()

    def get_goal_target_dates_in_period(self, start_date: datetime.date, end_date: datetime.date) -> set[datetime.date]:
        """Returns a set of dates within the period that have goal targets."""
        with self.Session() as session:
            query_result = session.query(func.date(Goal.target_date)).filter(
                Goal.target_date >= start_date,
                Goal.target_date <= end_date
            ).distinct().all()
            return {row[0] for row in query_result if row[0] is not None}

    def get_checkin_dates_in_period(self, start_date: datetime.date, end_date: datetime.date) -> set[datetime.date]:
        """Returns a set of dates within the period that have check-ins."""
        with self.Session() as session:
            query_result = session.query(func.date(GoalCheckIn.check_in_date)).filter(
                GoalCheckIn.check_in_date >= start_date,
                GoalCheckIn.check_in_date <= end_date
            ).distinct().all()
            return {row[0] for row in query_result if row[0] is not None}

    def get_goals_due_soon(self, days: int = 7) -> List[Goal]:
        with self.Session() as session:
            end_date = datetime.utcnow() + timedelta(days=days)
            return session.query(Goal).filter(
                Goal.target_date <= end_date,
                Goal.status != GoalStatus.COMPLETED
            ).all()

    def get_goal_progress(self, goal_id: int) -> Dict[str, Any]:
        with self.Session() as session:
            goal = session.query(Goal).filter(Goal.id == goal_id).first()
            if not goal:
                return None

            check_ins = session.query(GoalCheckIn).filter(
                GoalCheckIn.goal_id == goal_id
            ).order_by(GoalCheckIn.check_in_date.desc()).all()

            latest_check_in = check_ins[0] if check_ins else None
            total_check_ins = len(check_ins)

            return {
                'goal': goal,
                'latest_check_in': latest_check_in,
                'total_check_ins': total_check_ins,
                'check_in_history': check_ins
            }

    def link_habit_to_goal(self, goal_id: int, habit_id: int) -> bool:
        with self.Session() as session:
            goal = session.query(Goal).filter(Goal.id == goal_id).first()
            habit = session.query(Habit).filter(Habit.id == habit_id).first()
            
            if goal and habit:
                if habit not in goal.supporting_habits:
                    goal.supporting_habits.append(habit)
                    session.commit()
                    return True
                else:
                    return True
            return False

    def get_goals_with_category(self, limit: int = 0):
        """Get all goals, eager loading their parent goal."""
        with self.Session() as session:
            try:
                query = session.query(Goal).options(
                    joinedload(Goal.parent_goal)
                ).order_by(Goal.target_date.asc())
                if limit > 0:
                    query = query.limit(limit)
                return query.all()
            except Exception as e:
                logger.error(f"Error fetching all goals: {e}")
                return []

    def get_goal_with_details(self, goal_id: int) -> Optional[Goal]:
        """Retrieve a single goal with its related values, sub-goals, and supporting habits."""
        with self.Session() as session:
            try:
                return session.query(Goal).options(
                    joinedload(Goal.values),
                    joinedload(Goal.sub_goals),
                    joinedload(Goal.supporting_habits),
                    joinedload(Goal.check_ins)
                ).filter(Goal.id == goal_id).first()
            except Exception as e:
                logger.error(f"Error fetching goal with details for ID {goal_id}: {e}")
                return None

    def get_dashboard_summary_goals(self, limit: int = 5) -> List[Goal]:
        """Fetches a summary of active goals (Not Started, In Progress) for the dashboard, ordered by target_date."""
        with self.Session() as session:
            try:
                active_statuses = [GoalStatus.NOT_STARTED, GoalStatus.IN_PROGRESS]
                query = session.query(Goal).options(
                ).filter(Goal.status.in_(active_statuses)).order_by(Goal.target_date.asc())
                
                if limit > 0:
                    query = query.limit(limit)
                
                return query.all()
            except Exception as e:
                logger.error(f"Error fetching dashboard summary goals: {e}")
                return []

    def create_goal_check_in(self, goal_id: int, reflection: str, 
                           progress_percentage: float, notes: Optional[str] = None, 
                           contributing_habit_ids: Optional[List[int]] = None,
                           check_in_date: Optional[datetime] = None) -> GoalCheckIn:
        with self.Session() as session:
            goal = session.query(Goal).filter(Goal.id == goal_id).first()
            if not goal:
                raise ValueError(f"Goal with id {goal_id} not found.")
                
            final_check_in_date = check_in_date if check_in_date is not None else datetime.utcnow()

            check_in = GoalCheckIn(
                goal_id=goal_id,
                reflection=reflection,
                progress_percentage=progress_percentage,
                notes=notes,
                check_in_date=final_check_in_date
            )
            
            if contributing_habit_ids:
                contributing_habits = session.query(Habit).filter(Habit.id.in_(contributing_habit_ids)).all()
                check_in.contributing_habits.extend(contributing_habits)
            
            session.add(check_in)
            session.commit()
            session.refresh(check_in)
            return check_in

    def _get_all_descendant_ids(self, session: Session, goal_id: int) -> set[int]:
        """Helper to recursively fetch all descendant goal IDs."""
        descendant_ids = set()
        children_to_process = {goal_id} # Start with the initial goal itself if we want to include it
        
        # If we only want descendants, initialize children_to_process with direct children
        # direct_children_ids = {g.id for g in session.query(Goal.id).filter(Goal.parent_id == goal_id).all()}
        # children_to_process = direct_children_ids.copy()
        # descendant_ids.update(direct_children_ids)
        
        # Current implementation will gather IDs of goal_id AND its descendants.
        # For deleting, we usually want to delete the goal_id too.

        processed_for_children = set() # To avoid re-querying for children of already processed parents

        queue = [goal_id] # Start with the given goal ID
        ids_to_collect = set() # Will store the main goal and all its descendants

        while queue:
            current_parent_id = queue.pop(0)
            ids_to_collect.add(current_parent_id)

            # Find direct children of the current_parent_id
            direct_children = session.query(Goal.id).filter(Goal.parent_id == current_parent_id).all()
            for child_tuple in direct_children:
                child_id = child_tuple[0]
                if child_id not in ids_to_collect: # Avoid cycles and redundant additions
                    queue.append(child_id)
        return ids_to_collect

    def delete_goal(self, goal_id: int) -> bool:
        """Deletes a goal and all its descendants, along with associated check-ins."""
        with self.Session() as session:
            try:
                # Find the main goal to ensure it exists before proceeding
                main_goal = session.query(Goal).filter(Goal.id == goal_id).first()
                if not main_goal:
                    logger.warning(f"Goal with id {goal_id} not found for deletion.")
                    return False

                # Get all descendant IDs, including the main goal_id itself
                all_goal_ids_to_delete = self._get_all_descendant_ids(session, goal_id)
                
                if not all_goal_ids_to_delete:
                    # Should not happen if main_goal was found, as it includes itself
                    logger.warning(f"No goal IDs found for deletion for main goal_id {goal_id}.")
                    return False

                # 1. Delete associated GoalCheckIns
                # Ensure GoalCheckIn model is imported: from ..models.enhanced_models import GoalCheckIn
                session.query(GoalCheckIn).filter(GoalCheckIn.goal_id.in_(all_goal_ids_to_delete)).delete(synchronize_session=False)
                
                # 2. Delete the goals themselves
                # SQLAlchemy should handle cascade for many-to-many (values, supporting_habits) if configured in the Goal model.
                # If not, those links would need to be cleared manually before deleting goals.
                # Example: session.query(goal_values_association_table).filter(...).delete()
                # For now, assuming cascade on Goal model takes care of associations.
                
                # Fetch Goal objects to be deleted to leverage SQLAlchemy's cascade processing for relationships
                goals_to_delete_objects = session.query(Goal).filter(Goal.id.in_(all_goal_ids_to_delete)).all()
                for goal_obj in goals_to_delete_objects:
                    session.delete(goal_obj) # This should trigger cascades defined on Goal model relationships

                # If direct .delete() on query was preferred and cascades handled by DB:
                # session.query(Goal).filter(Goal.id.in_(all_goal_ids_to_delete)).delete(synchronize_session=False)
                
                session.commit()
                logger.info(f"Successfully deleted goal(s) with IDs: {all_goal_ids_to_delete}")
                return True
            except Exception as e:
                logger.error(f"Error deleting goal {goal_id} and its descendants: {e}", exc_info=True)
                session.rollback()
                return False 