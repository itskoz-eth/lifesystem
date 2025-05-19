from datetime import datetime
from typing import Optional, List
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QCheckBox, QSpinBox, QDoubleSpinBox,
                            QTextEdit, QScrollArea, QFrame, QMessageBox, QDateEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QColor, QPalette, QTextCharFormat
from ..models.enhanced_models import Habit, HabitEntry, CompletionType
from ..services.habit_service import HabitService

class HabitTrackingWidget(QFrame):
    """Widget for tracking a single habit."""
    def __init__(self, habit: Habit, habit_service: HabitService, selected_date: QDate, parent=None):
        super().__init__(parent)
        self.habit = habit
        self.habit_service = habit_service
        self.selected_date = selected_date
        self.entry_id_for_date: Optional[int] = None
        self.setup_ui()
        self.load_entry_for_date()
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 5px;
                padding: 10px;
            }
        """)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        name_label = QLabel(self.habit.name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(name_label)

        # Streak
        streak = self.habit_service.get_current_streak(self.habit.id)
        streak_label = QLabel(f"🔥 {streak} day streak")
        streak_label.setStyleSheet("color: black;")
        header_layout.addWidget(streak_label)
        layout.addLayout(header_layout)

        # Description
        if self.habit.description:
            desc_label = QLabel(self.habit.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666;")
            layout.addWidget(desc_label)

        # Completion controls
        controls_layout = QHBoxLayout()

        if self.habit.completion_type == CompletionType.BINARY:
            self.completed_check = QCheckBox("Completed")
            self.completed_check.stateChanged.connect(self.on_completion_changed)
            controls_layout.addWidget(self.completed_check)
        else:
            # For quantitative/duration habits
            self.value_spin = QDoubleSpinBox()
            self.value_spin.setRange(0, 1000)
            if self.habit.unit:
                self.value_spin.setSuffix(f" {self.habit.unit}")
            controls_layout.addWidget(self.value_spin)

            self.record_button = QPushButton("Record")
            self.record_button.clicked.connect(self.on_value_recorded)
            controls_layout.addWidget(self.record_button)

        layout.addLayout(controls_layout)

        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("How is this habit impacting your life and goals?")
        self.notes_edit.setMaximumHeight(60)
        layout.addWidget(self.notes_edit)

    def load_entry_for_date(self):
        """Load existing habit entry for the selected date."""
        py_date = self.selected_date.toPyDate()
        start_dt = datetime.combine(py_date, datetime.min.time())
        end_dt = datetime.combine(py_date, datetime.max.time())
        
        entries = self.habit_service.get_habit_entries(self.habit.id, start_dt, end_dt)
        if entries:
            entry = entries[0]
            self.entry_id_for_date = entry.id
            self.notes_edit.setText(entry.notes or "")
            if self.habit.completion_type == CompletionType.BINARY:
                self.completed_check.setChecked(entry.completed)
            else:
                self.value_spin.setValue(entry.value or 0)
            if self.habit.completion_type != CompletionType.BINARY:
                self.record_button.setText("Update")
        else:
            self.entry_id_for_date = None
            self.notes_edit.clear()
            if self.habit.completion_type == CompletionType.BINARY:
                self.completed_check.setChecked(False)
            else:
                self.value_spin.setValue(0)
            if self.habit.completion_type != CompletionType.BINARY:
                self.record_button.setText("Record")

    def on_completion_changed(self, state):
        self.record_or_update_entry(completed=(state == Qt.Checked))

    def on_value_recorded(self):
        self.record_or_update_entry(completed=True, value=self.value_spin.value())

    def record_or_update_entry(self, completed: bool, value: Optional[float] = None):
        """Record or update habit entry for the selected date."""
        py_date = self.selected_date.toPyDate()
        completion_datetime = datetime.combine(py_date, datetime.now().time())

        try:
            if self.entry_id_for_date is not None:
                new_entry = self.habit_service.record_habit_entry(
                    habit_id=self.habit.id,
                    completed=completed,
                    value=value,
                    notes=self.notes_edit.toPlainText(),
                    completion_date_override=completion_datetime
                )
                self.entry_id_for_date = new_entry.id
            else:
                new_entry = self.habit_service.record_habit_entry(
                    habit_id=self.habit.id,
                    completed=completed,
                    value=value,
                    notes=self.notes_edit.toPlainText(),
                    completion_date_override=completion_datetime
                )
                self.entry_id_for_date = new_entry.id
            if self.habit.completion_type != CompletionType.BINARY and hasattr(self, 'record_button'):
                self.record_button.setText("Update")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save entry: {str(e)}")
            if self.habit.completion_type == CompletionType.BINARY and hasattr(self, 'completed_check'):
                self.completed_check.setChecked(not completed)

class DailyTrackingView(QWidget):
    """View for tracking daily habit completions."""
    def __init__(self, habit_service: HabitService, parent=None):
        super().__init__(parent)
        self.habit_service = habit_service
        self.current_qdate = QDate.currentDate() # Initialize current date
        self.setup_ui()
        self.load_habits()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Daily Habit Tracking")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch() # Add stretch to push date controls to the right

        # Date Navigation
        header_layout.addWidget(QLabel("Date:"))
        
        self.prev_day_button = QPushButton("< Previous Day")
        self.prev_day_button.clicked.connect(self._go_to_previous_day)
        header_layout.addWidget(self.prev_day_button)

        self.date_display_label = QLabel(self.current_qdate.toString("MMMM d, yyyy"))
        self.date_display_label.setStyleSheet("font-size: 14px; padding: 0 10px;") # Add some padding
        header_layout.addWidget(self.date_display_label)

        self.next_day_button = QPushButton("Next Day >")
        self.next_day_button.clicked.connect(self._go_to_next_day)
        header_layout.addWidget(self.next_day_button)
        
        layout.addLayout(header_layout)

        # Scroll area for habit widgets
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.habits_container = QWidget()
        self.habits_layout = QVBoxLayout(self.habits_container)
        self.habits_layout.setSpacing(10)
        scroll.setWidget(self.habits_container)
        
        layout.addWidget(scroll)

    def _update_date_display_and_reload(self):
        self.date_display_label.setText(self.current_qdate.toString("MMMM d, yyyy"))
        self.load_habits()

    def _go_to_previous_day(self):
        self.current_qdate = self.current_qdate.addDays(-1)
        self._update_date_display_and_reload()

    def _go_to_next_day(self):
        self.current_qdate = self.current_qdate.addDays(1)
        self._update_date_display_and_reload()

    def load_habits(self):
        """Load active habits into the view."""
        # Clear existing widgets
        while self.habits_layout.count():
            item = self.habits_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        selected_qdate = self.current_qdate # Use the internal current_qdate
        habits = self.habit_service.get_active_habits()
        if not habits:
            no_habits_label = QLabel(f"No active habits to track for {selected_qdate.toString('MMMM d, yyyy')}.")
            no_habits_label.setAlignment(Qt.AlignCenter)
            self.habits_layout.addWidget(no_habits_label)
        else:
            for habit in habits:
                tracking_widget = HabitTrackingWidget(habit, self.habit_service, selected_qdate)
                self.habits_layout.addWidget(tracking_widget)

        self.habits_layout.addStretch() 