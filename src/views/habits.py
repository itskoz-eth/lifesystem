from datetime import datetime
from typing import Optional, List
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QTableWidget, QTableWidgetItem, QLabel, QComboBox,
                            QDialog, QFormLayout, QLineEdit, QTextEdit, QSpinBox,
                            QDoubleSpinBox, QMessageBox, QHeaderView, QCheckBox, QAbstractItemView,
                            QDialogButtonBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush
from ..models.enhanced_models import Habit, HabitEntry, HabitGoal, FrequencyType, CompletionType, HabitStatus
from ..models.category import Category
from ..services.habit_service import HabitService
from sqlalchemy.orm import Session, sessionmaker
import logging

logger = logging.getLogger(__name__)

class HabitDialog(QDialog):
    """Dialog for adding or editing a habit."""
    def __init__(self, parent=None, habit: Optional[Habit] = None):
        super().__init__(parent)
        self.habit = habit
        self.day_checkboxes: List[QCheckBox] = []
        self.setWindowTitle("Edit Habit" if habit else "Add New Habit")
        self.setMinimumWidth(400)
        self.setup_ui()
        if habit:
            self.load_habit_data()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.name_label = QLabel("&Name:")
        self.name_edit = QLineEdit()
        self.name_label.setBuddy(self.name_edit)
        layout.addRow(self.name_label, self.name_edit)

        self.description_label = QLabel("&Description:")
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_label.setBuddy(self.description_edit)
        layout.addRow(self.description_label, self.description_edit)

        self.frequency_label = QLabel("&Frequency:")
        self.frequency_combo = QComboBox()
        self.frequency_label.setBuddy(self.frequency_combo)
        for freq in FrequencyType:
            self.frequency_combo.addItem(freq.value.capitalize(), freq)
        layout.addRow(self.frequency_label, self.frequency_combo)
        self.frequency_combo.currentIndexChanged.connect(self.on_frequency_changed)

        self.specific_days_group = QGroupBox("Select Specific Days")
        specific_days_layout = QHBoxLayout()
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day_name in days:
            checkbox = QCheckBox(day_name)
            self.day_checkboxes.append(checkbox)
            specific_days_layout.addWidget(checkbox)
        self.specific_days_group.setLayout(specific_days_layout)
        layout.addRow(self.specific_days_group)
        self.specific_days_group.setVisible(False)

        self.completion_type_label = QLabel("&Completion Type:")
        self.completion_type_combo = QComboBox()
        self.completion_type_label.setBuddy(self.completion_type_combo)
        for comp_type in CompletionType:
            self.completion_type_combo.addItem(comp_type.value.capitalize(), comp_type)
        layout.addRow(self.completion_type_label, self.completion_type_combo)
        self.completion_type_combo.currentIndexChanged.connect(self.on_completion_type_changed)

        self.target_value_label = QLabel("&Target Value:")
        self.target_value_spin = QDoubleSpinBox()
        self.target_value_label.setBuddy(self.target_value_spin)
        self.target_value_spin.setRange(0, 10000)
        self.target_value_spin.setEnabled(False)
        layout.addRow(self.target_value_label, self.target_value_spin)

        self.unit_label = QLabel("&Unit:")
        self.unit_edit = QLineEdit()
        self.unit_label.setBuddy(self.unit_edit)
        self.unit_edit.setPlaceholderText("e.g., reps, minutes, km")
        self.unit_edit.setEnabled(False)
        layout.addRow(self.unit_label, self.unit_edit)
        
        self.status_label = QLabel("&Status:")
        self.status_combo = QComboBox()
        self.status_label.setBuddy(self.status_combo)
        for status in HabitStatus:
            self.status_combo.addItem(status.value.capitalize(), status)
        layout.addRow(self.status_label, self.status_combo)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
        self.setLayout(layout)

        QWidget.setTabOrder(self.name_edit, self.description_edit)
        QWidget.setTabOrder(self.description_edit, self.frequency_combo)
        QWidget.setTabOrder(self.frequency_combo, self.completion_type_combo)
        QWidget.setTabOrder(self.completion_type_combo, self.target_value_spin)
        QWidget.setTabOrder(self.target_value_spin, self.unit_edit)
        QWidget.setTabOrder(self.unit_edit, self.status_combo)
        QWidget.setTabOrder(self.status_combo, self.buttons)

    def on_completion_type_changed(self, index):
        comp_type = self.completion_type_combo.currentData()
        quantitative_or_duration = comp_type in [CompletionType.QUANTITATIVE, CompletionType.DURATION]
        self.target_value_spin.setEnabled(quantitative_or_duration)
        self.unit_edit.setEnabled(quantitative_or_duration)
        if not quantitative_or_duration:
            self.target_value_spin.setValue(0)
            self.unit_edit.clear()

    def on_frequency_changed(self, index):
        frequency_type = self.frequency_combo.currentData()
        is_specific_days = frequency_type == FrequencyType.SPECIFIC_DAYS
        self.specific_days_group.setVisible(is_specific_days)
        if not is_specific_days:
            for checkbox in self.day_checkboxes:
                checkbox.setChecked(False)

    def load_habit_data(self):
        """Populate dialog fields with existing habit data for editing."""
        if not self.habit: return
        self.name_edit.setText(self.habit.name)
        self.description_edit.setText(self.habit.description or "")
        
        freq_index = self.frequency_combo.findData(self.habit.frequency)
        if freq_index >= 0: self.frequency_combo.setCurrentIndex(freq_index)
        self.on_frequency_changed(freq_index)
        
        if self.habit.frequency == FrequencyType.SPECIFIC_DAYS and self.habit.specific_days_of_week:
            selected_days_indices = [int(d) for d in self.habit.specific_days_of_week.split(',') if d]
            for i, checkbox in enumerate(self.day_checkboxes):
                checkbox.setChecked(i in selected_days_indices)
        
        comp_type_index = self.completion_type_combo.findData(self.habit.completion_type)
        if comp_type_index >= 0: self.completion_type_combo.setCurrentIndex(comp_type_index)
        
        if self.habit.completion_type in [CompletionType.QUANTITATIVE, CompletionType.DURATION]:
            self.target_value_spin.setValue(self.habit.target_value or 0)
            self.unit_edit.setText(self.habit.unit or "")
            self.target_value_spin.setEnabled(True)
            self.unit_edit.setEnabled(True)
        else:
            self.target_value_spin.setValue(0)
            self.unit_edit.clear()
            
        status_index = self.status_combo.findData(self.habit.status)
        if status_index >= 0: self.status_combo.setCurrentIndex(status_index)

    def get_habit_data(self) -> dict:
        comp_type = self.completion_type_combo.currentData()
        quantitative_or_duration = comp_type in [CompletionType.QUANTITATIVE, CompletionType.DURATION]
        
        specific_days_str = None
        if self.frequency_combo.currentData() == FrequencyType.SPECIFIC_DAYS:
            selected_indices = [str(i) for i, cb in enumerate(self.day_checkboxes) if cb.isChecked()]
            if selected_indices:
                specific_days_str = ",".join(selected_indices)
            else:
                pass

        return {
            'name': self.name_edit.text(),
            'description': self.description_edit.toPlainText(),
            'frequency': self.frequency_combo.currentData(),
            'specific_days_of_week': specific_days_str,
            'completion_type': comp_type,
            'target_value': self.target_value_spin.value() if quantitative_or_duration else None,
            'unit': self.unit_edit.text() if quantitative_or_duration else None,
            'status': self.status_combo.currentData()
        }

class HabitsView(QWidget):
    """Main view for managing habits."""
    def __init__(self, habit_service: HabitService, parent=None):
        super().__init__(parent)
        self.habit_service = habit_service
        self.setup_ui()
        self.load_habits()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Manage Habits")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        add_button = QPushButton("Add New Habit")
        add_button.clicked.connect(self.add_habit)
        header_layout.addWidget(add_button)
        
        layout.addLayout(header_layout)

        # Habits Table
        self.habits_table = QTableWidget()
        self.habits_table.setAlternatingRowColors(True)
        self.habits_table.setColumnCount(6)  # New: Name, Frequency, Type, Streak, Completion, Status
        self.habits_table.setHorizontalHeaderLabels([
            "Name", "Frequency", "Type", "Current Streak", # Removed "Category"
            "Completion Rate (30d)", "Status"
        ])
        self.habits_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.habits_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.habits_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.habits_table)

        # Action Buttons for selected habit
        action_button_layout = QHBoxLayout()
        self.edit_habit_button = QPushButton("Edit Selected Habit")
        self.edit_habit_button.clicked.connect(self.edit_selected_habit)
        action_button_layout.addWidget(self.edit_habit_button)

        self.delete_habit_button = QPushButton("Delete Selected Habit")
        self.delete_habit_button.clicked.connect(self.delete_selected_habit)
        action_button_layout.addWidget(self.delete_habit_button)
        layout.addLayout(action_button_layout)

    def load_habits(self):
        try:
            habits = self.habit_service.get_all_habits() # This no longer loads category
            self.habits_table.setRowCount(0)

            for habit in habits:
                row_position = self.habits_table.rowCount()
                self.habits_table.insertRow(row_position)
                
                name_item = QTableWidgetItem(habit.name)
                name_item.setData(Qt.UserRole, habit.id) # Store habit ID
                
                frequency_display = habit.frequency.value.capitalize()
                if habit.frequency == FrequencyType.SPECIFIC_DAYS:
                    if habit.specific_days_of_week:
                        days_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                        selected_indices = [int(d) for d in habit.specific_days_of_week.split(',') if d]
                        days_str = ", ".join([days_map[i] for i in selected_indices])
                        frequency_display = f"Days: {days_str}"
                    else:
                        frequency_display = "Days: None"
                
                streak = self.habit_service.get_current_streak(habit.id)
                completion_rate = self.habit_service.get_completion_rate(habit.id, 30)

                self.habits_table.setItem(row_position, 0, name_item)
                self.habits_table.setItem(row_position, 1, QTableWidgetItem(frequency_display)) # Index shifted
                self.habits_table.setItem(row_position, 2, QTableWidgetItem(habit.completion_type.value.capitalize())) # Index shifted
                self.habits_table.setItem(row_position, 3, QTableWidgetItem(f"{streak}")) # Index shifted
                self.habits_table.setItem(row_position, 4, QTableWidgetItem(f"{completion_rate:.1f}%")) # Index shifted
                self.habits_table.setItem(row_position, 5, QTableWidgetItem(habit.status.value.capitalize())) # Index shifted

                status_color = QColor("#d4edda") if habit.status == HabitStatus.ACTIVE else QColor("#f8d7da")
                for col in range(self.habits_table.columnCount()):
                    self.habits_table.item(row_position, col).setBackground(status_color)

        except Exception as e:
            logger.error(f"Error loading habits: {str(e)}")
            QMessageBox.critical(self, "Error", f"Could not load habits: {str(e)}")

    def get_selected_habit_id(self) -> Optional[int]:
        """Get the ID of the selected habit in the table."""
        selected_items = self.habits_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            return self.habits_table.item(row, 0).data(Qt.UserRole)
        return None

    def add_habit(self):
        dialog = HabitDialog(self) # Removed categories=categories
        if dialog.exec_() == QDialog.Accepted:
            habit_data = dialog.get_habit_data()
            if not habit_data['name'].strip():
                QMessageBox.warning(self, "Input Error", "Habit name cannot be empty.")
                return
            try:
                self.habit_service.create_habit(**habit_data) # category_id is no longer in habit_data
                self.load_habits()
            except Exception as e:
                logger.error(f"Error creating habit: {e}")
                QMessageBox.critical(self, "Error", f"Failed to create habit: {str(e)}")

    def edit_selected_habit(self):
        habit_id = self.get_selected_habit_id()
        if habit_id is None: return
        
        habit_to_edit = self.habit_service.get_habit(habit_id) # Does not load category
        if not habit_to_edit:
            QMessageBox.critical(self, "Error", "Habit not found or could not be loaded.")
            return

        dialog = HabitDialog(self, habit=habit_to_edit) # Removed categories=categories
        if dialog.exec_() == QDialog.Accepted:
            habit_data = dialog.get_habit_data()
            if not habit_data['name'].strip():
                QMessageBox.warning(self, "Input Error", "Habit name cannot be empty.")
                return
            try:
                self.habit_service.update_habit(habit_id, **habit_data) # category_id is no longer in habit_data
                self.load_habits()
            except Exception as e:
                logger.error(f"Error updating habit: {e}")
                QMessageBox.critical(self, "Error", f"Failed to update habit: {str(e)}")

    def delete_selected_habit(self):
        habit_id = self.get_selected_habit_id()
        if habit_id is None:
            QMessageBox.warning(self, "Selection Error", "Please select a habit to delete.")
            return
        
        habit_to_delete = self.habit_service.get_habit(habit_id)
        if not habit_to_delete:
             QMessageBox.critical(self, "Error", "Habit not found for deletion.")
             return

        reply = QMessageBox.question(self, "Confirm Deletion", 
                                   f"Are you sure you want to delete the habit '{habit_to_delete.name}'?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.habit_service.delete_habit(habit_id)
                self.load_habits()
                QMessageBox.information(self, "Success", "Habit deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete habit: {str(e)}")

    # record_completion can be removed if not directly used in this view anymore
    # def record_completion(self, habit_id: int): ... 