"""
UI components for the Life System application.
"""

from .goals import GoalsView
from .values import ValuesView
# from .categories import CategoriesView # REMOVED
# from .reflections import ReflectionView # Commented out
from .habits import HabitsView
from .daily_tracking import DailyTrackingView
from .habit_analytics import HabitAnalyticsView
from .integrated_dashboard_view import IntegratedDashboardView
from .check_in_dialog import CheckInDialog

__all__ = [
    'GoalsView',
    'ValuesView',
    # 'CategoriesView', # REMOVED
    # 'ReflectionView', # Commented out
    'HabitsView',
    'DailyTrackingView',
    'HabitAnalyticsView',
    'IntegratedDashboardView',
    'CheckInDialog'
] 