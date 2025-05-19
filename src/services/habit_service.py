from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, sessionmaker, joinedload
from sqlalchemy import and_, func
from ..models.enhanced_models import Habit, HabitEntry, HabitGoal, FrequencyType, CompletionType, HabitStatus, Goal
import logging

logger = logging.getLogger(__name__)

class HabitService:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    def create_habit(self, name: str, description: str, frequency: FrequencyType,
                    completion_type: CompletionType, status: HabitStatus,
                    target_value: Optional[float] = None,
                    unit: Optional[str] = None,
                    specific_days_of_week: Optional[str] = None) -> Habit:
        """Create a new habit."""
        with self.Session() as session:
            habit = Habit(
                name=name,
                description=description,
                frequency=frequency,
                specific_days_of_week=specific_days_of_week,
                completion_type=completion_type,
                status=status,
                target_value=target_value,
                unit=unit
            )
            logger.debug(f"Creating Habit object: {vars(habit)}")
            logger.debug(f"Does habit object have 'is_active'? {'is_active' in vars(habit)}")
            logger.debug(f"Does habit object have 'active'? {'active' in vars(habit)}")
            
            session.add(habit)
            session.commit()
            session.refresh(habit)
            return habit

    def get_habit(self, habit_id: int) -> Optional[Habit]:
        """Get a habit by ID."""
        with self.Session() as session:
            return session.query(Habit).filter(Habit.id == habit_id).first()

    def get_all_habits(self) -> List[Habit]:
        """Get all habits."""
        with self.Session() as session:
            return session.query(Habit).all()

    def get_active_habits(self) -> List[Habit]:
        """Get all active habits (without preloading relationships)."""
        with self.Session() as session:
            return session.query(Habit).filter(Habit.status == HabitStatus.ACTIVE).all()

    def get_active_habits_with_goals(self) -> List[Habit]:
        """Get all active habits, eager loading their supporting_goals."""
        with self.Session() as session:
            return session.query(Habit).options(
                joinedload(Habit.supporting_goals)
            ).filter(Habit.status == HabitStatus.ACTIVE).all()

    def update_habit(self, habit_id: int, **kwargs) -> Optional[Habit]:
        """Update a habit's attributes."""
        with self.Session() as session:
            habit = session.query(Habit).filter(Habit.id == habit_id).first()
            if habit:
                # Ensure specific_days_of_week is cleared if frequency is not SPECIFIC_DAYS
                if 'frequency' in kwargs and kwargs['frequency'] != FrequencyType.SPECIFIC_DAYS:
                    kwargs['specific_days_of_week'] = None
                elif habit.frequency == FrequencyType.SPECIFIC_DAYS and 'frequency' not in kwargs and 'specific_days_of_week' not in kwargs:
                    # If frequency is specific days and not being changed, but specific_days_of_week is not provided in kwargs,
                    # it means no days were selected, so it should be cleared (set to None).
                    # However, get_habit_data in HabitDialog should provide None if no days are checked.
                    # This explicit clear might be redundant if dialog logic is robust.
                    pass # Let specific_days_of_week pass through from kwargs or remain as is if not in kwargs

                for key, value in kwargs.items():
                    # Handle enums from string values if necessary, though dialog sends enum members
                    if key == "frequency" and not isinstance(value, FrequencyType):
                        value = FrequencyType(value)
                    elif key == "completion_type" and not isinstance(value, CompletionType):
                        value = CompletionType(value)
                    elif key == "status" and not isinstance(value, HabitStatus):
                        value = HabitStatus(value)
                    setattr(habit, key, value)
                session.commit()
                session.refresh(habit)
            return habit

    def delete_habit(self, habit_id: int) -> bool:
        """Delete a habit."""
        with self.Session() as session:
            habit = session.query(Habit).filter(Habit.id == habit_id).first()
            if habit:
                session.delete(habit)
                session.commit()
                return True
            return False

    def record_habit_entry(self, habit_id: int, completed: bool, 
                          value: Optional[float] = None, 
                          notes: Optional[str] = None, 
                          completion_date_override: Optional[datetime] = None) -> HabitEntry:
        """Record or update a habit entry for a specific date."""
        with self.Session() as session:
            target_date = completion_date_override.date() if completion_date_override else datetime.utcnow().date()
            
            # Try to find an existing entry for this habit on this specific date
            existing_entry = session.query(HabitEntry).filter(
                HabitEntry.habit_id == habit_id,
                func.date(HabitEntry.completion_date) == target_date
            ).first()

            if existing_entry:
                # Update existing entry
                existing_entry.completed = completed
                existing_entry.value = value
                existing_entry.notes = notes
                existing_entry.completion_date = completion_date_override or existing_entry.completion_date # Keep original time if not overridden
                existing_entry.updated_at = datetime.utcnow()
                entry_to_return = existing_entry
            else:
                # Create new entry
                habit = session.query(Habit).filter(Habit.id == habit_id).first()
                if not habit:
                    raise ValueError(f"Habit with id {habit_id} not found.")
                
                new_entry = HabitEntry(
                    habit_id=habit_id,
                    completed=completed,
                    value=value,
                    notes=notes,
                    completion_date=completion_date_override or datetime.combine(target_date, datetime.utcnow().time())
                )
                session.add(new_entry)
                entry_to_return = new_entry
            
            session.commit()
            session.refresh(entry_to_return)
            return entry_to_return

    def get_habit_entries(self, habit_id: int, start_date: datetime,
                         end_date: datetime) -> List[HabitEntry]:
        """Get habit entries for a specific date range."""
        with self.Session() as session:
            return session.query(HabitEntry).filter(
                and_(
                    HabitEntry.habit_id == habit_id,
                    HabitEntry.completion_date >= start_date,
                    HabitEntry.completion_date <= end_date
                )
            ).order_by(HabitEntry.completion_date.desc()).all()

    def get_habit_entries_for_date_with_habit(self, entry_date: datetime.date) -> List[HabitEntry]:
        """Get habit entries for a specific date, eager loading the associated habit."""
        with self.Session() as session:
            return session.query(HabitEntry).options(
                joinedload(HabitEntry.habit)
            ).filter(func.date(HabitEntry.completion_date) == entry_date).all()

    def get_habit_entry_dates_in_period(self, start_date: datetime.date, end_date: datetime.date) -> set[datetime.date]:
        """Returns a set of dates within the period that have habit entries."""
        with self.Session() as session:
            query_result = session.query(func.date(HabitEntry.completion_date)).filter(
                HabitEntry.completion_date >= start_date,
                HabitEntry.completion_date <= end_date,
                HabitEntry.completed == True # Optional: only count completed habits for markers
            ).distinct().all()
            return {row[0] for row in query_result if row[0] is not None}

    def get_all_entries_for_habit_in_period(self, habit_id: int, start_date: datetime.date, end_date: datetime.date) -> List[HabitEntry]:
        """Returns all habit entries for a specific habit within the period."""
        with self.Session() as session:
            return session.query(HabitEntry).filter(
                HabitEntry.habit_id == habit_id,
                func.date(HabitEntry.completion_date) >= start_date,
                func.date(HabitEntry.completion_date) <= end_date
            ).order_by(HabitEntry.completion_date).all()

    def is_habit_due_on_date(self, habit: Habit, target_date: datetime.date) -> bool:
        """Check if a habit is due on a specific date based on its frequency."""
        if habit.status != HabitStatus.ACTIVE:
            return False

        if habit.frequency == FrequencyType.DAILY:
            return True
        elif habit.frequency == FrequencyType.WEEKLY:
            # Assuming weekly habits are due on the same day of the week as their creation date
            # This could be refined if habits have a specific 'start day' for weekly frequency
            return habit.created_at.weekday() == target_date.weekday()
        elif habit.frequency == FrequencyType.MONTHLY:
            # Assuming monthly habits are due on the same day of the month as their creation
            # This could be refined for end-of-month logic or specific day of month
            return habit.created_at.day == target_date.day
        elif habit.frequency == FrequencyType.SPECIFIC_DAYS:
            if not habit.specific_days_of_week:
                return False
            due_days = [int(d) for d in habit.specific_days_of_week.split(',') if d]
            return target_date.weekday() in due_days # Monday is 0, Sunday is 6
        return False

    def get_entry_for_habit_on_date(self, habit_id: int, target_date: datetime.date) -> Optional[HabitEntry]:
        """Retrieve a habit entry for a specific habit on a specific date."""
        with self.Session() as session:
            return session.query(HabitEntry).filter(
                HabitEntry.habit_id == habit_id,
                func.date(HabitEntry.completion_date) == target_date
            ).first()

    def get_dashboard_habit_status_for_display(self, habit: Habit, target_date: datetime.date) -> str:
        """Determines a display string for habit status on a given date for the dashboard."""
        if not self.is_habit_due_on_date(habit, target_date):
            return "Not Due Today"

        entry = self.get_entry_for_habit_on_date(habit.id, target_date)

        if entry:
            if entry.completed:
                return "Completed"
            elif habit.completion_type == CompletionType.QUANTITATIVE or habit.completion_type == CompletionType.DURATION:
                # For quantitative/duration, if an entry exists but not 'completed', it might be partially done.
                # 'completed' flag in HabitEntry should ideally be set true only when target is met.
                # If not completed, it implies it's still pending or partially done.
                return "In Progress" 
            else: # Binary, entry exists but not completed
                return "Pending" # Or "Missed" if past due and not done - this logic might be too complex for here
        else:
            # No entry, but it is due
            return "Pending"

    def get_current_streak(self, habit_id: int) -> int:
        """Calculate the current streak for a habit."""
        with self.Session() as session:
            today = datetime.utcnow().date()
            entries = session.query(HabitEntry).filter(
                HabitEntry.habit_id == habit_id,
                HabitEntry.completed == True,
                func.date(HabitEntry.completion_date) <= today
            ).order_by(HabitEntry.completion_date.desc()).all()
            
            streak = 0
            expected_date = today
            entry_dates = {entry.completion_date.date() for entry in entries}

            while expected_date in entry_dates:
                streak += 1
                expected_date -= timedelta(days=1)
                
            return streak

    def get_completion_rate(self, habit_id: int, days: int = 30) -> float:
        """Calculate the completion rate for a habit over the last N days, 
           or since habit creation if younger than N days, considering habit frequency."""
        with self.Session() as session:
            habit = session.query(Habit).filter(Habit.id == habit_id).first()
            if not habit:
                logger.warning(f"get_completion_rate called for non-existent habit_id: {habit_id}")
                return 0.0

            today_date = datetime.utcnow().date()
            n_days_ago = today_date - timedelta(days=days -1) # -1 to include today in N-day period
            habit_creation_date = habit.created_at.date()
            
            calculation_start_date = max(n_days_ago, habit_creation_date)
            
            if calculation_start_date > today_date: 
                # Habit created in the future or some other edge case.
                logger.debug(f"Habit {habit_id}: Calculation start date {calculation_start_date} is after today {today_date}. Rate: 0.0")
                return 0.0
            
            # Calculate the number of days the habit was actually due in the period
            due_days_count = 0
            current_date_in_loop = calculation_start_date
            while current_date_in_loop <= today_date:
                if self.is_habit_due_on_date(habit, current_date_in_loop):
                    due_days_count += 1
                current_date_in_loop += timedelta(days=1)

            if due_days_count == 0:
                logger.debug(f"Habit {habit_id}: No due days found in the period {calculation_start_date} to {today_date}. Rate: 0.0")
                return 0.0 # Avoid division by zero if habit was not due at all in the period

            # Get entries within this actual calculation period
            entries = session.query(HabitEntry).filter(
                HabitEntry.habit_id == habit_id,
                HabitEntry.completed == True,
                func.date(HabitEntry.completion_date) >= calculation_start_date,
                func.date(HabitEntry.completion_date) <= today_date 
            ).all()
            
            # Count unique completed days within the actual period
            # This implicitly handles cases where a habit might be logged multiple times on a due date
            # but only counts as one completion for that specific date.
            completed_dates_in_period = {entry.completion_date.date() for entry in entries}
            
            # Filter these completed dates to only those where the habit was also due
            # This is important if a habit was completed on a day it wasn't strictly "due"
            # (e.g. user chose to do it anyway). We only want to count completions on due dates.
            # However, the problem description is "completion rate", which usually implies
            # (times done / times it should have been done).
            # The current `is_habit_due_on_date` logic should correctly define the "should have been done" dates.
            # So, completed_count should be the number of due dates on which it was completed.
            
            actually_completed_on_due_dates = 0
            for completed_date in completed_dates_in_period:
                # We must ensure this completed_date falls within our calculation_start_date and today_date,
                # which is already guaranteed by the SQL query for 'entries'.
                # Then, check if this specific completed_date was a due date.
                if self.is_habit_due_on_date(habit, completed_date): # This check might be redundant if entries only created for due days.
                                                                # But good for robustness.
                    actually_completed_on_due_dates +=1
            
            # The `completed_count` should be `actually_completed_on_due_dates`
            completed_count = actually_completed_on_due_dates
            
            rate = (completed_count / due_days_count) * 100
            logger.debug(f"Habit {habit_id}: Completed {completed_count} times out of {due_days_count} due days in period. Rate: {rate:.2f}%")
            return rate

    def get_completion_trend(self, habit_id: int, days: int = 7) -> List[bool]:
        """Get completion status (True/False) for the last N days for trend visualization."""
        trend_data = []
        today = datetime.utcnow().date()
        with self.Session() as session:
            for i in range(days -1, -1, -1): # Iterate from (days-1) down to 0 (e.g., 6 down to 0 for 7 days)
                current_date = today - timedelta(days=i)
                entry = session.query(HabitEntry).filter(
                    HabitEntry.habit_id == habit_id,
                    func.date(HabitEntry.completion_date) == current_date,
                    HabitEntry.completed == True
                ).first()
                trend_data.append(bool(entry))
        return trend_data

    def create_habit_goal(self, habit_id: int, target_date: datetime,
                         target_value: Optional[float] = None,
                         description: Optional[str] = None) -> HabitGoal:
        """Create a new goal for a habit."""
        with self.Session() as session:
            goal = HabitGoal(
                habit_id=habit_id,
                target_date=target_date,
                target_value=target_value,
                goal_description=description
            )
            session.add(goal)
            session.commit()
            session.refresh(goal)
            return goal

    def get_habit_goals(self, habit_id: int) -> List[HabitGoal]:
        """Get all goals for a habit."""
        with self.Session() as session:
            return session.query(HabitGoal).filter(
                HabitGoal.habit_id == habit_id
            ).all()

    def update_goal_completion(self, goal_id: int, completed: bool) -> Optional[HabitGoal]:
        """Update a goal's completion status."""
        with self.Session() as session:
            goal = session.query(HabitGoal).filter(HabitGoal.id == goal_id).first()
            if goal:
                goal.completed = completed
                session.commit()
                session.refresh(goal)
            return goal 