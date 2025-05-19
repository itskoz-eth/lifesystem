from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QListWidget, QListWidgetItem, QDialog, QFormLayout, 
                            QLineEdit, QTextEdit, QComboBox, QDateEdit, 
                            QDialogButtonBox, QMessageBox, QScrollArea, QTreeWidget, QTreeWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QTextCharFormat
from ..models.enhanced_models import Goal, GoalStatus, Habit
from ..models.value import Value
from ..services.goal_service import GoalService
from ..services.habit_service import HabitService
from ..services.value_service import ValueService
from .check_in_dialog import CheckInDialog
import logging
from typing import Optional, List
import datetime

logger = logging.getLogger(__name__)

class GoalDialog(QDialog):
    def __init__(self, parent=None, goal: Optional[Goal] = None, 
                 all_values: Optional[List[Value]] = None, 
                 all_active_habits: Optional[List[Habit]] = None,
                 eligible_parent_goals: Optional[List[tuple]] = None,
                 target_date_override: Optional[datetime.date] = None):
        super().__init__(parent)
        self.goal = goal
        self.all_values = all_values if all_values else []
        self.all_active_habits = all_active_habits if all_active_habits else []
        self.eligible_parent_goals = eligible_parent_goals if eligible_parent_goals else []
        self.target_date_override = target_date_override
        
        self.setWindowTitle("Edit Goal" if goal else "Add New Goal")
        self.setMinimumWidth(500)
        self.setup_ui()
        if goal:
            self.load_goal_data()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self) # Main layout for the dialog
        form_layout = QFormLayout() # For the top form part
        
        self.name_label = QLabel("&Name:")
        self.name_input = QLineEdit()
        self.name_label.setBuddy(self.name_input)
        form_layout.addRow(self.name_label, self.name_input)

        self.description_label = QLabel("&Description:")
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_label.setBuddy(self.description_input)
        form_layout.addRow(self.description_label, self.description_input)
        
        self.target_date_label = QLabel("&Target Date:")
        initial_date = QDate.currentDate()
        if self.target_date_override:
            initial_date = QDate(self.target_date_override.year, 
                                 self.target_date_override.month, 
                                 self.target_date_override.day)
        elif self.goal and self.goal.target_date: 
             initial_date = QDate(self.goal.target_date.year, 
                                 self.goal.target_date.month, 
                                 self.goal.target_date.day)
        self.target_date_input = QDateEdit(initial_date)
        self.target_date_input.setCalendarPopup(True)
        
        # Set weekend day names and dates to black for the QDateEdit calendar
        calendar_widget = self.target_date_input.calendarWidget()
        if calendar_widget: # Check if calendar widget exists
            black_text_format = QTextCharFormat()
            black_text_format.setForeground(QColor("black"))
            calendar_widget.setWeekdayTextFormat(Qt.Saturday, black_text_format)
            calendar_widget.setWeekdayTextFormat(Qt.Sunday, black_text_format)
            
        self.target_date_label.setBuddy(self.target_date_input)
        form_layout.addRow(self.target_date_label, self.target_date_input)
        
        self.status_label = QLabel("&Status:")
        self.status_input = QComboBox()
        self.status_label.setBuddy(self.status_input)
        for status_enum_member in GoalStatus:
            self.status_input.addItem(status_enum_member.value.replace('_', ' ').title(), status_enum_member)
        form_layout.addRow(self.status_label, self.status_input)

        self.parent_goal_label = QLabel("&Parent Goal:")
        self.parent_goal_combo = QComboBox()
        self.parent_goal_label.setBuddy(self.parent_goal_combo)
        self.parent_goal_combo.addItem("No Parent", None)
        for pg_id, pg_name, _ in self.eligible_parent_goals:
            self.parent_goal_combo.addItem(pg_name, pg_id)
        form_layout.addRow(self.parent_goal_label, self.parent_goal_combo)

        main_layout.addLayout(form_layout) # Add the form layout to the main VBox layout

        self.values_label = QLabel("Link to &Values:")
        self.values_list_widget = QListWidget()
        self.values_list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.values_list_widget.setMaximumHeight(100)
        self.values_label.setBuddy(self.values_list_widget)
        for val in self.all_values:
            item = QListWidgetItem(val.name)
            item.setData(Qt.UserRole, val.id)
            self.values_list_widget.addItem(item)
        main_layout.addWidget(self.values_label) # Add label then widget
        main_layout.addWidget(self.values_list_widget)

        self.habits_label = QLabel("Supporting &Habits:")
        self.habits_list_widget = QListWidget()
        self.habits_list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.habits_list_widget.setMaximumHeight(100)
        self.habits_label.setBuddy(self.habits_list_widget)
        for habit in self.all_active_habits:
            item = QListWidgetItem(habit.name)
            item.setData(Qt.UserRole, habit.id)
            self.habits_list_widget.addItem(item)
        main_layout.addWidget(self.habits_label) # Add label then widget
        main_layout.addWidget(self.habits_list_widget)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        main_layout.addWidget(self.buttons)
        
        self.setLayout(main_layout) # Set main_layout as the dialog's layout

        # Set Tab Order
        QWidget.setTabOrder(self.name_input, self.description_input)
        QWidget.setTabOrder(self.description_input, self.target_date_input)
        QWidget.setTabOrder(self.target_date_input, self.status_input)
        QWidget.setTabOrder(self.status_input, self.parent_goal_combo)
        QWidget.setTabOrder(self.parent_goal_combo, self.values_list_widget)
        QWidget.setTabOrder(self.values_list_widget, self.habits_list_widget)
    
    def load_goal_data(self):
        self.name_input.setText(self.goal.name)
        self.description_input.setText(self.goal.description or "")
        
        # Target date is now set in setup_ui based on override or goal data
        # if self.goal.target_date:
        #     qdate = QDate(self.goal.target_date.year, self.goal.target_date.month, self.goal.target_date.day)
        #     self.target_date_input.setDate(qdate)
        
        status_index = self.status_input.findData(self.goal.status)
        if status_index >= 0:
            self.status_input.setCurrentIndex(status_index)

        # Pre-select parent goal
        if self.goal and self.goal.parent_id:
            parent_index = self.parent_goal_combo.findData(self.goal.parent_id)
            if parent_index >= 0:
                self.parent_goal_combo.setCurrentIndex(parent_index)
        else:
            self.parent_goal_combo.setCurrentIndex(0) # Default to "No Parent"

        # Pre-select linked Values
        if self.goal.values:
            linked_value_ids = {val.id for val in self.goal.values}
            for i in range(self.values_list_widget.count()):
                item = self.values_list_widget.item(i)
                if item.data(Qt.UserRole) in linked_value_ids:
                    item.setSelected(True)

        # Pre-select linked Habits
        if self.goal.supporting_habits:
            linked_habit_ids = {hab.id for hab in self.goal.supporting_habits}
            for i in range(self.habits_list_widget.count()):
                item = self.habits_list_widget.item(i)
                if item.data(Qt.UserRole) in linked_habit_ids:
                    item.setSelected(True)

    def get_goal_form_data(self) -> dict:
        selected_value_ids = [self.values_list_widget.item(i).data(Qt.UserRole) 
                              for i in range(self.values_list_widget.count()) if self.values_list_widget.item(i).isSelected()]
        selected_habit_ids = [self.habits_list_widget.item(i).data(Qt.UserRole) 
                              for i in range(self.habits_list_widget.count()) if self.habits_list_widget.item(i).isSelected()]

        return {
            'name': self.name_input.text(),
            'description': self.description_input.toPlainText(),
            'target_date': self.target_date_input.date().toPyDate(),
            'status': self.status_input.currentData(),
            'parent_id': self.parent_goal_combo.currentData(),
            'linked_value_ids': selected_value_ids,
            'linked_habit_ids': selected_habit_ids
        }

class GoalsView(QWidget):
    def __init__(self, goal_service: GoalService, habit_service: HabitService, value_service: ValueService):
        super().__init__()
        self.goal_service = goal_service
        self.habit_service = habit_service
        self.value_service = value_service
        self._all_goals_for_parent_selection_cache: List[tuple] = [] # Cache (id, name, parent_id)
        self.setup_ui()
        self.load_goals()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Goals")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        add_button = QPushButton("Add New Goal")
        add_button.clicked.connect(self.show_add_goal_dialog)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(add_button)
        layout.addLayout(header)
        
        # Goals Tree
        self.goals_tree = QTreeWidget()
        self.goals_tree.setAlternatingRowColors(True)
        self.goals_tree.setColumnCount(3) # Goal, Status, Target Date
        self.goals_tree.setHeaderLabels(["Goal", "Status", "Target Date"])
        self.goals_tree.header().setSectionResizeMode(0, QHeaderView.Stretch) # Stretch Goal name column
        self.goals_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.goals_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout.addWidget(self.goals_tree)
        
        # Buttons for selected goal
        button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Edit Goal")
        self.delete_button = QPushButton("Delete Goal")
        self.check_in_button = QPushButton("Check-In")
        self.edit_button.clicked.connect(self.edit_selected_goal)
        self.delete_button.clicked.connect(self.delete_selected_goal)
        self.check_in_button.clicked.connect(self.show_check_in_dialog)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.check_in_button)
        layout.addLayout(button_layout)
    
    def load_goals(self):
        try:
            all_goals_from_service = self.goal_service.get_goals_with_category() # This loads parent_goal object

            self.goals_tree.clear()
            
            # Sort goals: top-level goals first, then by name. This helps in processing.
            # Goals with no parent_id come first.
            sorted_goals = sorted(all_goals_from_service, key=lambda g: (g.parent_id is not None, g.name))

            goal_to_tree_item_map = {} # Maps goal.id to QTreeWidgetItem

            for goal_obj in sorted_goals:
                goal_name = goal_obj.name
                status_str = goal_obj.status.value.replace('_', ' ').title() if goal_obj.status else "N/A"
                target_date_str = goal_obj.target_date.strftime('%Y-%m-%d') if goal_obj.target_date else "No Date"

                item_texts = [goal_name, status_str, target_date_str]
                
                # Determine if it's a top-level item or child
                parent_tree_item = None
                if goal_obj.parent_id and goal_obj.parent_id in goal_to_tree_item_map:
                    parent_tree_item = goal_to_tree_item_map[goal_obj.parent_id]

                if parent_tree_item:
                    tree_item = QTreeWidgetItem(parent_tree_item, item_texts)
                else:
                    # If parent_id is set but parent_tree_item is not found (e.g. parent not processed yet or bad data)
                    # it will become a top-level item. Sorting should mitigate this for valid hierarchies.
                    tree_item = QTreeWidgetItem(self.goals_tree, item_texts)
                
                tree_item.setData(0, Qt.UserRole, goal_obj) # Store the full Goal object
                goal_to_tree_item_map[goal_obj.id] = tree_item

                # Apply styling
                status_color_hex = "#CCCCCC"; text_color_hex = "#000000" # Default/Not Started
                if goal_obj.status == GoalStatus.IN_PROGRESS: status_color_hex = "#FFF3CD"; text_color_hex = "#664D03"
                elif goal_obj.status == GoalStatus.COMPLETED: status_color_hex = "#D1E7DD"; text_color_hex = "#0A3622"
                elif goal_obj.status == GoalStatus.CANCELLED: status_color_hex = "#F8D7DA"; text_color_hex = "#58151C"
                elif goal_obj.status == GoalStatus.ON_HOLD: status_color_hex = "#E2E3E5"; text_color_hex = "#41464B" 
                
                bg_color = QColor(status_color_hex)
                text_color = QColor(text_color_hex)
                for i in range(self.goals_tree.columnCount()):
                    tree_item.setBackground(i, bg_color)
                    tree_item.setForeground(i, text_color)

            self.goals_tree.expandAll()

            # Update cache for parent selection using a dedicated service call
            self._all_goals_for_parent_selection_cache = self.goal_service.get_all_goals_for_parent_selection()
            
        except Exception as e:
            logger.error(f"Error loading goals into tree: {str(e)}", exc_info=True) # Added exc_info
            QMessageBox.critical(self, "Error", f"Failed to load goals: {str(e)}")

    def get_selected_goal(self) -> Optional[Goal]:
        selected_items = self.goals_tree.selectedItems()
        if not selected_items:
            return None
        # The data stored is the full Goal object
        goal_object = selected_items[0].data(0, Qt.UserRole)
        if not isinstance(goal_object, Goal):
            # This case should ideally not happen if data is set correctly
            logger.error("Selected item does not contain a valid Goal object.")
            return None
        
        # Use service to get goal with details necessary for editing/check-in,
        # passing the ID of the goal object.
        return self.goal_service.get_goal_with_details(goal_object.id)
    
    def _fetch_all_values_for_dialog(self) -> List[Value]:
        try:
            return self.value_service.get_all_values()
        except Exception as e:
            logger.error(f"Error fetching values for GoalDialog: {e}")
            QMessageBox.warning(self, "Error", "Could not fetch values for the dialog.")
            return []
    
    def _fetch_all_active_habits_for_dialog(self) -> List[Habit]:
        # This already uses habit_service, which is good.
        try:
            return self.habit_service.get_active_habits()
        except Exception as e:
            logger.error(f"Error fetching active habits for GoalDialog: {e}")
            QMessageBox.warning(self, "Error", "Could not fetch active habits for the dialog.")
            return []
    
    def _get_all_descendant_ids(self, goal_id: int, all_goals_tuples: List[tuple]) -> set[int]:
        descendants = set()
        children_to_process = {goal_id}
        processed_ids = set()
        while children_to_process:
            current_parent_id = children_to_process.pop()
            if current_parent_id in processed_ids: continue
            processed_ids.add(current_parent_id)
            for g_id, _, g_parent_id in all_goals_tuples:
                if g_parent_id == current_parent_id:
                    if g_id not in descendants:
                        descendants.add(g_id)
                        children_to_process.add(g_id)
        return descendants

    def show_add_goal_dialog(self, target_date_override: Optional[datetime.date] = None):
        try:
            all_values = self._fetch_all_values_for_dialog()
            all_active_habits = self._fetch_all_active_habits_for_dialog()
            
            eligible_parents = self._all_goals_for_parent_selection_cache
            
            dialog = GoalDialog(
                parent=self,
                all_values=all_values,
                all_active_habits=all_active_habits,
                eligible_parent_goals=eligible_parents,
                target_date_override=target_date_override 
            )
            
            if dialog.exec_() == QDialog.Accepted:
                goal_data = dialog.get_goal_form_data()
                if not goal_data['name'].strip():
                    QMessageBox.warning(self, "Input Error", "Goal name cannot be empty.")
                    return

                # Call goal_service to create the goal
                created_goal = self.goal_service.create_goal(
                    name=goal_data['name'],
                    description=goal_data['description'],
                    target_date=datetime.datetime.combine(goal_data['target_date'], datetime.datetime.min.time()), # Ensure datetime
                    status=goal_data['status'],
                    parent_id=goal_data['parent_id'],
                    linked_value_ids=goal_data['linked_value_ids'],
                    linked_habit_ids=goal_data['linked_habit_ids']
                )
                if created_goal:
                    self.load_goals() # Refresh the tree
                    QMessageBox.information(self, "Success", "Goal added successfully.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to add goal.")
        except Exception as e:
            logger.error(f"Error in show_add_goal_dialog: {str(e)}")
            QMessageBox.critical(self, "Dialog Error", f"Could not open or process add goal dialog: {str(e)}")

    def edit_selected_goal(self):
        selected_goal = self.get_selected_goal() # Uses service, gets Goal object with details
        if not selected_goal:
            QMessageBox.warning(self, "No Selection", "Please select a goal to edit.")
            return
        
        try:
            all_values = self._fetch_all_values_for_dialog()
            all_active_habits = self._fetch_all_active_habits_for_dialog()

            # Filter out the current goal and its descendants from eligible parents
            all_goals_tuples = self._all_goals_for_parent_selection_cache
            descendant_ids = self._get_all_descendant_ids(selected_goal.id, all_goals_tuples)
            ineligible_parent_ids = descendant_ids.union({selected_goal.id})
            eligible_parents = [(gid, name, pid) for gid, name, pid in all_goals_tuples if gid not in ineligible_parent_ids]

            dialog = GoalDialog(
                parent=self, 
                goal=selected_goal, 
                all_values=all_values, 
                all_active_habits=all_active_habits,
                eligible_parent_goals=eligible_parents
            )

            if dialog.exec_() == QDialog.Accepted:
                goal_data = dialog.get_goal_form_data()
                if not goal_data['name'].strip():
                    QMessageBox.warning(self, "Input Error", "Goal name cannot be empty.")
                    return

                updated_goal = self.goal_service.update_goal(
                    goal_id=selected_goal.id,
                    name=goal_data['name'],
                    description=goal_data['description'],
                    target_date=datetime.datetime.combine(goal_data['target_date'], datetime.datetime.min.time()), # Ensure datetime
                    status=goal_data['status'],
                    parent_id=goal_data['parent_id'],
                    linked_value_ids=goal_data['linked_value_ids'],
                    linked_habit_ids=goal_data['linked_habit_ids']
                )
                if updated_goal:
                    self.load_goals() # Refresh the tree
                    QMessageBox.information(self, "Success", "Goal updated successfully.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to update goal.")
        except Exception as e:
            logger.error(f"Error in edit_selected_goal: {str(e)}")
            QMessageBox.critical(self, "Dialog Error", f"Could not open or process edit goal dialog: {str(e)}")

    def delete_selected_goal(self):
        selected_goal = self.get_selected_goal() # Uses service, gets Goal object
        if not selected_goal:
            QMessageBox.warning(self, "No Selection", "Please select a goal to delete.")
            return

        reply = QMessageBox.question(self, 'Confirm Delete', 
                                     f"Are you sure you want to delete the goal \"{selected_goal.name}\" and all its sub-goals?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.goal_service.delete_goal(selected_goal.id): # Assuming delete_goal handles sub-goals or cascade works
                self.load_goals() # Refresh tree
                QMessageBox.information(self, "Success", "Goal deleted successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete goal.")

    def show_check_in_dialog(self):
        selected_goal = self.get_selected_goal() # Uses service
        if not selected_goal:
            QMessageBox.warning(self, "No Selection", "Please select a goal to check-in.")
            return

        # Fetch habits that could be linked to this check-in (active habits)
        # GoalDialog already fetches active habits, can reuse that or fetch here
        contributing_habits_list = self.habit_service.get_active_habits()

        dialog = CheckInDialog(self, goal=selected_goal, habit_service=self.habit_service, all_contributing_habits=contributing_habits_list)
        if dialog.exec_() == QDialog.Accepted:
            check_in_data = dialog.get_check_in_data()
            try:
                self.goal_service.create_check_in(
                    goal_id=selected_goal.id,
                    reflection=check_in_data['reflection'],
                    progress_percentage=check_in_data['progress'],
                    notes=check_in_data['notes'],
                    contributing_habit_ids=check_in_data['contributing_habit_ids'],
                    check_in_date=datetime.datetime.combine(check_in_data['check_in_date'], datetime.datetime.min.time())
                )
                QMessageBox.information(self, "Success", "Check-in recorded.")
                # self.load_goals() # Optional: Refresh goals view if check-ins affect goal display immediately
            except Exception as e:
                logger.error(f"Error creating check-in: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to record check-in: {str(e)}") 