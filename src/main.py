import sys
import logging
import os # Import os for path joining
from logging.handlers import RotatingFileHandler # Added for log rotation
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                            QLineEdit, QTextEdit, QComboBox, QDateEdit, QListWidget,
                            QFormLayout, QMessageBox, QDialog, QScrollArea)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon, QColor
from .models import init_db
from sqlalchemy.orm import Session
from .views.goals import GoalsView
from .views.values import ValuesView
# from .views.categories import CategoriesView
# from .views.reflections import ReflectionView # Commented out
from .views.habits import HabitsView
from .views.daily_tracking import DailyTrackingView
from .views.habit_analytics import HabitAnalyticsView
from .views.calendar_view import CalendarView
from .views.integrated_dashboard_view import IntegratedDashboardView
from .services.habit_service import HabitService
from .services.goal_service import GoalService
from .services.value_service import ValueService
from .services.dashboard_service import DashboardService

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs') # Place logs outside src
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, 'life_system.log')

# Basic config for console, then add file handler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()] # Default to console
)

# Add a rotating file handler
file_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=2, mode='a')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logging.getLogger().addHandler(file_handler) # Add to root logger to catch all logs

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Initializing MainWindow...")
        self.setWindowTitle("Life System - Running")
        self.setMinimumSize(1200, 800)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                font-size: 14px;
            }
        """)
        
        # Initialize database
        logger.info("Initializing database...")
        self.engine = init_db()
        logger.info("Database initialization complete")
        
        # Create a session
        # self.db_session = Session(self.engine) # This line might be vestigial if all views/services use engine

        # Initialize services
        self.habit_service = HabitService(self.engine)
        self.goal_service = GoalService(self.engine)
        self.value_service = ValueService(self.engine)
        self.dashboard_service = DashboardService(self.engine)
        
        # Create main widget and layout
        logger.info("Setting up UI...")
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create sidebar
        sidebar = QWidget()
        sidebar.setObjectName("leftSidebar")
        sidebar.setMaximumWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        
        # Add app title to sidebar
        app_title = QLabel("LIFE SYSTEM")
        app_title.setObjectName("appTitle")
        app_title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(app_title)
        
        # Add sidebar buttons
        self.sidebar_buttons = {}
        self.sidebar_buttons["Dashboard"] = self.add_sidebar_button(sidebar_layout, "Dashboard", self.show_dashboard)
        self.sidebar_buttons["Goals"] = self.add_sidebar_button(sidebar_layout, "Goals", self.show_goals)
        self.sidebar_buttons["Values"] = self.add_sidebar_button(sidebar_layout, "Values", self.show_values)
        # self.sidebar_buttons["Categories"] = self.add_sidebar_button(sidebar_layout, "Categories", self.show_categories) # REMOVED
        # self.sidebar_buttons["Reflections"] = self.add_sidebar_button(sidebar_layout, "Reflections", self.show_reflections) # Commented out
        self.sidebar_buttons["Habits"] = self.add_sidebar_button(sidebar_layout, "Habits", self.show_habits)
        self.sidebar_buttons["Daily Tracking"] = self.add_sidebar_button(sidebar_layout, "Daily Tracking", self.show_daily_tracking)
        self.sidebar_buttons["Habit Analytics"] = self.add_sidebar_button(sidebar_layout, "Habit Analytics", self.show_habit_analytics)
        self.sidebar_buttons["Calendar"] = self.add_sidebar_button(sidebar_layout, "Calendar", self.show_calendar)
        
        # Add stretch to push buttons to top
        sidebar_layout.addStretch()
        
        # Add exit button at the bottom
        self.add_sidebar_button(sidebar_layout, "Exit", self.close)
        
        # Create scrollable main content area
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.content_area = QStackedWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.content_area)
        content_layout.addWidget(scroll_area)
        
        # Add widgets to layout
        layout.addWidget(sidebar)
        layout.addWidget(content_container, 1)  # stretch factor 1
        
        # Set initial view
        logger.info("Setting initial view...")
        self.show_goals()
        logger.info("MainWindow initialization complete")
    
    def _update_active_sidebar_button(self, active_button_text: str):
        for text, button in self.sidebar_buttons.items():
            if text == active_button_text:
                button.setProperty("cssClass", "activeView")
            else:
                button.setProperty("cssClass", "") # Clear class
            # Re-apply stylesheet to make property changes take effect (Qt trick)
            button.style().unpolish(button)
            button.style().polish(button)
    
    def clear_content_area(self):
        while self.content_area.count() > 0:
            widget = self.content_area.widget(0)
            self.content_area.removeWidget(widget)
            widget.deleteLater()
    
    def add_sidebar_button(self, layout, text, callback) -> QPushButton:
        button = QPushButton(text)
        button.clicked.connect(callback)
        layout.addWidget(button)
        return button
    
    def show_goals(self):
        self._update_active_sidebar_button("Goals")
        logger.info("Loading Goals view...")
        self.clear_content_area()
        goals_view = GoalsView(self.goal_service, self.habit_service, self.value_service)
        self.content_area.addWidget(goals_view)
        logger.info("Goals view loaded")
    
    def show_values(self):
        self._update_active_sidebar_button("Values")
        logger.info("Loading Values view...")
        self.clear_content_area()
        values_view = ValuesView(self.value_service)
        self.content_area.addWidget(values_view)
        logger.info("Values view loaded")
    
    # def show_categories(self): # REMOVED METHOD
    #     self._update_active_sidebar_button("Categories")
    #     logger.info("Loading Categories view...")
    #     self.clear_content_area()
    #     categories_view = CategoriesView(self.engine)
    #     self.content_area.addWidget(categories_view)
    #     logger.info("Categories view loaded")
    
    def show_habits(self):
        self._update_active_sidebar_button("Habits")
        logger.info("Loading Habits view...")
        self.clear_content_area()
        habits_view = HabitsView(self.habit_service)
        self.content_area.addWidget(habits_view)
        logger.info("Habits view loaded")
    
    def show_daily_tracking(self):
        self._update_active_sidebar_button("Daily Tracking")
        logger.info("Loading Daily Tracking view...")
        self.clear_content_area()
        daily_tracking_view = DailyTrackingView(self.habit_service)
        self.content_area.addWidget(daily_tracking_view)
        logger.info("Daily Tracking view loaded")
    
    def show_habit_analytics(self):
        self._update_active_sidebar_button("Habit Analytics")
        logger.info("Loading Habit Analytics view...")
        self.clear_content_area()
        habit_analytics_view = HabitAnalyticsView(self.habit_service)
        self.content_area.addWidget(habit_analytics_view)
        logger.info("Habit Analytics view loaded")
    
    def show_calendar(self):
        self._update_active_sidebar_button("Calendar")
        logger.info("Loading Calendar view...")
        self.clear_content_area()
        calendar_view = CalendarView(self.goal_service, self.habit_service, self.dashboard_service)
        self.content_area.addWidget(calendar_view)
        logger.info("Calendar view loaded")

    def show_dashboard(self):
        self._update_active_sidebar_button("Dashboard")
        logger.info("Loading Integrated Dashboard view...")
        self.clear_content_area()
        dashboard_view = IntegratedDashboardView(
            self.habit_service, 
            self.goal_service, 
            self.value_service, 
            self.dashboard_service
        )
        self.content_area.addWidget(dashboard_view)
        logger.info("Integrated Dashboard view loaded")

def main():
    logger.info("Starting application...")
    app = QApplication(sys.argv)

    # Load global stylesheet
    stylesheet_path = os.path.join(os.path.dirname(__file__), "assets", "styles.qss")
    try:
        with open(stylesheet_path, "r") as f:
            app.setStyleSheet(f.read())
            logger.info(f"Stylesheet loaded from {stylesheet_path}")
    except FileNotFoundError:
        logger.warning(f"Stylesheet not found at {stylesheet_path}. Using default styles.")
    except Exception as e:
        logger.error(f"Error loading stylesheet: {e}")

    window = MainWindow()
    window.show()
    logger.info("Application window shown, entering event loop")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 