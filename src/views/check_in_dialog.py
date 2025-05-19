from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
                            QLineEdit, QTextEdit, QDateEdit, QDoubleSpinBox, 
                            QPushButton, QDialogButtonBox, QListWidget, QListWidgetItem, QCheckBox, QWidget)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
from typing import Optional, List
from ..models.enhanced_models import Goal, Habit, GoalStatus # Import GoalStatus too for display
from ..services.habit_service import HabitService

class CheckInDialog(QDialog):
    def __init__(self, goal: Goal, habit_service: HabitService, parent=None):
        super().__init__(parent)
        self.goal = goal
        self.habit_service = habit_service
        self.setWindowTitle(f"Check-in for Goal: {self.goal.name}")
        self.setMinimumWidth(450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.goal_name_label_desc = QLabel("Goal:") # Non-interactive, so no mnemonic needed here
        self.goal_name_label = QLabel(f"<b>{self.goal.name}</b><br><small>Current Status: {self.goal.status.value.replace('_',' ').title()}</small>")
        self.goal_name_label.setWordWrap(True)
        # self.goal_name_label_desc.setBuddy(self.goal_name_label) # Buddy not needed for a display QLabel
        form_layout.addRow(self.goal_name_label_desc, self.goal_name_label)

        self.date_label = QLabel("&Date:")
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_label.setBuddy(self.date_edit)
        form_layout.addRow(self.date_label, self.date_edit)

        self.progress_label = QLabel("&Progress:")
        self.progress_spinbox = QDoubleSpinBox()
        self.progress_label.setBuddy(self.progress_spinbox)
        self.progress_spinbox.setRange(0.0, 100.0)
        self.progress_spinbox.setSuffix(" %")
        latest_progress = 0.0 
        if self.goal.check_ins:
            latest_check_in = sorted(self.goal.check_ins, key=lambda ci: ci.check_in_date, reverse=True)[0]
            if latest_check_in and latest_check_in.progress_percentage is not None:
                latest_progress = latest_check_in.progress_percentage
        self.progress_spinbox.setValue(latest_progress) 
        form_layout.addRow(self.progress_label, self.progress_spinbox)

        self.reflection_label = QLabel("&Reflection:")
        self.reflection_edit = QTextEdit()
        self.reflection_label.setBuddy(self.reflection_edit)
        self.reflection_edit.setPlaceholderText("How is it going? Any challenges or wins?")
        form_layout.addRow(self.reflection_label, self.reflection_edit)

        self.habits_label = QLabel("&Contributing Habits:")
        self.habits_list_widget = QListWidget()
        self.habits_label.setBuddy(self.habits_list_widget)
        self.habits_list_widget.setSelectionMode(QListWidget.MultiSelection)
        active_habits = self.habit_service.get_active_habits()
        if active_habits:
            for habit in active_habits:
                item = QListWidgetItem(habit.name)
                item.setData(Qt.UserRole, habit.id)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.habits_list_widget.addItem(item)
        else:
            self.habits_list_widget.addItem(QListWidgetItem("No active habits to link."))
            self.habits_list_widget.setEnabled(False)
        form_layout.addRow(self.habits_label, self.habits_list_widget)
        
        layout.addLayout(form_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

        # Set Tab Order
        QWidget.setTabOrder(self.date_edit, self.progress_spinbox)
        QWidget.setTabOrder(self.progress_spinbox, self.reflection_edit)
        QWidget.setTabOrder(self.reflection_edit, self.habits_list_widget)
        # QWidget.setTabOrder(self.habits_list_widget, self.buttons)

    def get_check_in_data(self) -> dict:
        reflection = self.reflection_edit.toPlainText()
        progress = self.progress_spinbox.value()
        check_in_date = self.date_edit.date().toPyDate()
        
        selected_habit_ids = []
        for i in range(self.habits_list_widget.count()):
            item = self.habits_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                habit_id = item.data(Qt.UserRole)
                if habit_id is not None:
                    selected_habit_ids.append(habit_id)

        return {
            'goal_id': self.goal.id,
            'reflection': reflection,
            'progress_percentage': progress,
            'check_in_date': datetime.combine(check_in_date, datetime.min.time()), # Store as datetime
            'contributing_habit_ids': selected_habit_ids,
            'notes': '' # Placeholder for now
        } 