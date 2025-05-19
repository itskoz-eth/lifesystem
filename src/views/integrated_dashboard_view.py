from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit,
                            QComboBox, QFrame, QScrollArea, QProgressBar, QTextEdit, QPushButton)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont # Added for potential font adjustments
from datetime import datetime, timedelta, date as DateObject # Import DateObject
from ..services.habit_service import HabitService
from ..services.goal_service import GoalService
from ..services.value_service import ValueService
from ..services.dashboard_service import DashboardService
from ..models.enhanced_models import Habit, CompletionType, FrequencyType # Import Habit, CompletionType, and FrequencyType for type hinting
from .note_history_dialog import NoteHistoryDialog # Import NoteHistoryDialog

# Matplotlib imports for trend chart (REMOVE THESE if chart is removed)
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# import matplotlib.pyplot as plt 

# Placeholder for individual habit progress widget
class HabitProgressWidget(QFrame):
    def __init__(self, habit: Habit, display_progress_value: int, progress_bar_format: str, streak: int, parent=None):
        super().__init__(parent)
        self.habit = habit # Store the full habit object
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        # Stylesheet updated to remove QProgressBar specific parts, handled globally now.
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
            }
            QLabel {
                font-size: 12px;
            }
            QLabel[cssClass="habitName"] {
                font-weight: bold;
                font-size: 14px;
            }
            QLabel[cssClass="streakLabel"] {
                font-size: 11px; 
                color: #555;
            }
        """)
        main_layout = QVBoxLayout(self) # Changed back to QVBoxLayout as chart is removed
        main_layout.setSpacing(6)

        # Info: Name, Progress, Streak, Linked Goals
        name_label = QLabel(habit.name)
        name_label.setProperty("cssClass", "habitName")
        main_layout.addWidget(name_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(display_progress_value)
        self.progress_bar.setFormat(progress_bar_format)
        main_layout.addWidget(self.progress_bar)
        
        streak_label = QLabel(f"Streak: {streak} days")
        streak_label.setProperty("cssClass", "streakLabel")
        main_layout.addWidget(streak_label)
        
        if self.habit.supporting_goals:
            goals_text = "Supports: " + ", ".join([g.name for g in self.habit.supporting_goals[:2]])
            if len(self.habit.supporting_goals) > 2:
                goals_text += "..."
            linked_goals_label = QLabel(goals_text)
            linked_goals_label.setStyleSheet("font-size: 10px; color: #777;")
            linked_goals_label.setWordWrap(True)
            main_layout.addWidget(linked_goals_label)
        main_layout.addStretch(1)

        # Trend chart removed
        # self.trend_canvas = FigureCanvas(Figure(figsize=(1.5, 0.8)))
        # self._plot_trend(trend_data)
        # main_layout.addWidget(self.trend_canvas, 1)

    # _plot_trend method can be removed

# --- New Section Widgets to be defined here --- 
class WhiteboardWidget(QFrame):
    def __init__(self, dashboard_service: DashboardService, parent=None):
        super().__init__(parent)
        self.dashboard_service = dashboard_service
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setObjectName("whiteboardWidget")
        # Basic layout
        layout = QVBoxLayout(self)
        label = QLabel("Whiteboard / Quick Notes")
        label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 5px;")
        self.note_area = QTextEdit()
        self.note_area.setPlaceholderText("Jot down your thoughts for today...")
        self.history_button = QPushButton("View History") # New button
        self.save_button = QPushButton("Save Note")
        self.clear_button = QPushButton("Clear Note")

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.history_button) # Add history button
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.save_button)

        layout.addWidget(label)
        layout.addWidget(self.note_area)
        layout.addLayout(button_layout)

        self.save_button.clicked.connect(self.save_note)
        self.clear_button.clicked.connect(self.clear_note)
        self.history_button.clicked.connect(self.show_history) # Connect new button
        self.load_note()

    def load_note(self):
        today_date_obj = DateObject.today() # Use DateObject for today's date
        latest_note = self.dashboard_service.get_latest_note_for_date(today_date_obj)
        if latest_note and latest_note.content:
            self.note_area.setText(latest_note.content)
        else:
            self.note_area.setPlaceholderText("Jot down your thoughts for today...") # Updated placeholder
            self.note_area.clear()

    def save_note(self):
        content = self.note_area.toPlainText()
        if not content.strip(): # Don't save empty notes
            # Optionally, provide feedback to the user
            return 
        today_date_obj = DateObject.today()
        self.dashboard_service.save_note_for_date(content, today_date_obj)
        # Add user feedback, e.g., status bar message or simple dialog
        # After saving, we could clear the note area or reload to show it, 
        # but since multiple notes can exist for a day, clearing might be better for new input.
        self.note_area.setPlaceholderText("Note saved! Add another or clear.")
        # self.load_note() # Reloading would show the same note. Better to clear for next input.

    def clear_note(self):
        self.note_area.clear()
        self.note_area.setPlaceholderText("Jot down your thoughts for today...")
        # This button does not delete from DB anymore. Deletion will be handled in history view.

    def show_history(self): # New method to show the history dialog
        dialog = NoteHistoryDialog(self.dashboard_service, self)
        dialog.exec_()
        # Optionally, refresh the current note in the whiteboard if the history dialog could have changed it
        # For now, load_note will fetch the latest for today, which is fine.
        self.load_note() # Refresh today's note view after history interaction

class ValuesSummaryWidget(QFrame):
    def __init__(self, value_service: ValueService, parent=None):
        super().__init__(parent)
        self.value_service = value_service
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setObjectName("valuesSummaryWidget")
        layout = QVBoxLayout(self)
        label = QLabel("Core Values")
        label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 5px;")
        self.values_display_layout = QVBoxLayout() # To hold value labels
        layout.addWidget(label)
        layout.addLayout(self.values_display_layout)
        layout.addStretch(1)
        self.load_values()

    def load_values(self):
        # Clear previous values
        while self.values_display_layout.count():
            child = self.values_display_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        values = self.value_service.get_all_values()
        if values:
            for value in values: # Display all values
                value_text = f"<b>{value.name}</b>"
                if value.description:
                    value_text += f": {value.description}"
                value_label = QLabel(value_text)
                value_label.setWordWrap(True)
                self.values_display_layout.addWidget(value_label)
        else:
            self.values_display_layout.addWidget(QLabel("No values defined yet."))

class GoalsSummaryWidget(QFrame):
    def __init__(self, goal_service: GoalService, parent=None):
        super().__init__(parent)
        self.goal_service = goal_service
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setObjectName("goalsSummaryWidget")
        layout = QVBoxLayout(self)
        label = QLabel("Strategic Goals")
        label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 5px;")
        self.goals_display_layout = QVBoxLayout() # Use a layout to add goal widgets
        layout.addWidget(label)
        layout.addLayout(self.goals_display_layout)
        layout.addStretch(1)
        self.load_goals()

    def load_goals(self):
        # Clear previous goals
        while self.goals_display_layout.count():
            child = self.goals_display_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        summary_goals = self.goal_service.get_dashboard_summary_goals(limit=0) # Fetch all active goals
        print(f"[DEBUG] GoalsSummaryWidget: Fetched summary_goals: {summary_goals}") # Temporary debug print
        
        if summary_goals:
            for goal in summary_goals:
                status_str = goal.status.value.replace('_', ' ').title() if goal.status else "N/A"
                target_date_str = goal.target_date.strftime('%Y-%m-%d') if goal.target_date else "No Target Date"
                
                goal_info = f"{goal.name}\nStatus: {status_str} | Target: {target_date_str}"
                goal_label = QLabel(goal_info)
                goal_label.setWordWrap(True)
                # Add some padding or margin to goal_label if needed via stylesheet or by adding to another layout
                self.goals_display_layout.addWidget(goal_label)
                # You could add a separator here if desired, e.g., QFrame with HLine
        else:
            no_goals_label = QLabel("No active goals to display.")
            no_goals_label.setAlignment(Qt.AlignCenter)
            self.goals_display_layout.addWidget(no_goals_label)

class HabitsSummaryWidget(QFrame):
    def __init__(self, habit_service: HabitService, parent=None):
        super().__init__(parent)
        self.habit_service = habit_service
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setObjectName("habitsSummaryWidget")
        layout = QVBoxLayout(self)
        label = QLabel("Daily Habits")
        label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 5px;")
        self.habits_display_layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(self.habits_display_layout)
        layout.addStretch(1)
        self.load_habits()

    def load_habits(self):
        # Clear previous habits
        while self.habits_display_layout.count():
            child = self.habits_display_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        active_habits = self.habit_service.get_active_habits()
        # today = datetime.utcnow().date() # No longer needed for this display

        if active_habits:
            for habit in active_habits: # Display all active habits
                # streak = self.habit_service.get_current_streak(habit.id) # No longer needed
                # today_status = self.habit_service.get_dashboard_habit_status_for_display(habit, today) # No longer needed
                
                frequency_display = habit.frequency.value.capitalize()
                if habit.frequency == FrequencyType.SPECIFIC_DAYS:
                    if habit.specific_days_of_week:
                        days_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                        try:
                            selected_indices = [int(d) for d in habit.specific_days_of_week.split(',') if d.strip().isdigit()]
                            days_str = ", ".join([days_map[i] for i in selected_indices if 0 <= i < len(days_map)])
                            frequency_display = f"Days: {days_str}" if days_str else "Days: None Specified"
                        except ValueError:
                            frequency_display = "Days: Invalid Specific Days Format"
                    else:
                        frequency_display = "Days: None Specified"

                # habit_label_text = f"{habit.name} (Streak: {streak}d)\nStatus: {today_status}" # Old display
                habit_label_text = f"<b>{habit.name}</b>\nFrequency: {frequency_display}"
                habit_label = QLabel(habit_label_text)
                habit_label.setWordWrap(True) # In case name is long
                self.habits_display_layout.addWidget(habit_label)
        else:
            self.habits_display_layout.addWidget(QLabel("No active habits found."))

class IntegratedDashboardView(QWidget):
    def __init__(self, habit_service: HabitService, goal_service: GoalService, value_service: ValueService, dashboard_service: DashboardService, parent=None):
        super().__init__(parent)
        self.habit_service = habit_service
        self.goal_service = goal_service
        self.value_service = value_service
        self.dashboard_service = dashboard_service
        
        self.setup_ui()
        # self.load_dashboard_data() # Call this after UI setup, but it's now handled by individual widgets
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15) # Add some spacing between sections
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #f0f0f0; }")
        
        dashboard_widget_container = QWidget() # A container widget for the scroll area
        sections_layout = QVBoxLayout(dashboard_widget_container) # Main layout for content is Vertical
        sections_layout.setContentsMargins(10, 10, 10, 10)
        sections_layout.setSpacing(20)

        # 1. Whiteboard Section (full width)
        self.whiteboard_section = WhiteboardWidget(self.dashboard_service)
        sections_layout.addWidget(self.whiteboard_section)

        # Container for horizontal summary sections
        horizontal_summary_container = QWidget()
        horizontal_layout = QHBoxLayout(horizontal_summary_container)
        horizontal_layout.setContentsMargins(0,0,0,0) # No margins for the inner container itself
        horizontal_layout.setSpacing(20) # Spacing between horizontal items

        # 2. Values Section
        self.values_section = ValuesSummaryWidget(self.value_service)
        horizontal_layout.addWidget(self.values_section)

        # 3. Goals Section
        self.goals_section = GoalsSummaryWidget(self.goal_service)
        horizontal_layout.addWidget(self.goals_section)

        # 4. Habits Section
        self.habits_section = HabitsSummaryWidget(self.habit_service)
        horizontal_layout.addWidget(self.habits_section)
        
        # horizontal_layout.addStretch(1) # Optional: if you want them to bunch to the left

        sections_layout.addWidget(horizontal_summary_container) # Add the horizontal container to the main vertical layout

        sections_layout.addStretch(1) # Pushes content to the top if not filling scroll area
        
        scroll_area.setWidget(dashboard_widget_container)
        main_layout.addWidget(scroll_area)

    # The old load_dashboard_data and clear_dashboard are largely superseded by individual widget load methods
    # A refresh method might be useful if data can change while view is open.
    def refresh_dashboard_data(self):
        self.whiteboard_section.load_note()
        self.values_section.load_values()
        self.goals_section.load_goals()
        self.habits_section.load_habits()

# The old HabitProgressWidget can be removed if no longer directly used by IntegratedDashboardView
# or if its functionality is fully incorporated into HabitsSummaryWidget.
# For now, it's left in case parts are reusable for HabitsSummaryWidget internal display. 