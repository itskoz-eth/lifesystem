from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget,
                            QLabel, QPushButton, QScrollArea, QFrame, QComboBox,
                            QInputDialog, QMessageBox, QFormLayout, QCheckBox,
                            QDoubleSpinBox, QLineEdit, QDialogButtonBox, QDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QPalette, QTextCharFormat, QFont
from datetime import datetime, timedelta, date as DateObject
from typing import List, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from ..services.goal_service import GoalService
from ..services.habit_service import HabitService
from ..services.dashboard_service import DashboardService
from ..models.enhanced_models import Goal, Habit, HabitEntry, CompletionType, GoalStatus
from ..models.value import Value
from ..models.category import Category
from ..models.whiteboard_note import DatedNote
from ..views.goals import GoalDialog
import logging
import calendar

logger = logging.getLogger(__name__)

class QuickHabitEntryDialog(QDialog):
    def __init__(self, habit_to_record: Habit, selected_date: datetime.date, parent=None):
        super().__init__(parent)
        self.habit = habit_to_record
        self.selected_date = selected_date
        self.setWindowTitle(f"Log Entry for {self.habit.name}")
        self.setMinimumWidth(350)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        layout.addRow(QLabel(f"<b>Habit:</b> {self.habit.name}"))
        layout.addRow(QLabel(f"<b>Date:</b> {self.selected_date.strftime('%Y-%m-%d')}"))

        self.completed_checkbox = QCheckBox("&Completed")
        self.completed_checkbox.setChecked(True)
        layout.addRow("", self.completed_checkbox)

        self.value_label_desc = QLabel("&Value:")
        self.value_spinbox = QDoubleSpinBox()
        self.value_label_desc.setBuddy(self.value_spinbox)
        self.value_spinbox.setRange(0, 100000)
        unit_text = f" ({self.habit.unit})" if self.habit.unit else ""
        self.value_unit_label = QLabel(unit_text)
        
        value_layout = QHBoxLayout()
        value_layout.addWidget(self.value_spinbox)
        value_layout.addWidget(self.value_unit_label)

        if self.habit.completion_type in [CompletionType.QUANTITATIVE, CompletionType.DURATION]:
            self.value_label_desc.setVisible(True)
            self.value_spinbox.setVisible(True)
            self.value_unit_label.setVisible(True)
            if self.habit.target_value:
                self.value_spinbox.setValue(self.habit.target_value)
        else:
            self.value_label_desc.setVisible(False)
            self.value_spinbox.setVisible(False)
            self.value_spinbox.setValue(0)
            self.value_unit_label.setVisible(False)
        
        layout.addRow(self.value_label_desc, value_layout)

        self.notes_label = QLabel("&Notes:")
        self.notes_edit = QLineEdit()
        self.notes_label.setBuddy(self.notes_edit)
        self.notes_edit.setPlaceholderText("Optional notes...")
        layout.addRow(self.notes_label, self.notes_edit)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
        self.setLayout(layout)

        QWidget.setTabOrder(self.completed_checkbox, self.value_spinbox)
        QWidget.setTabOrder(self.value_spinbox, self.notes_edit)

    def get_entry_data(self) -> dict:
        data = {
            'completed': self.completed_checkbox.isChecked(),
            'notes': self.notes_edit.text() or None,
            'value': None
        }
        if self.habit.completion_type in [CompletionType.QUANTITATIVE, CompletionType.DURATION] and self.value_spinbox.isVisible():
            data['value'] = self.value_spinbox.value()
        return data

class CalendarEventWidget(QFrame):
    def __init__(self, title, date_or_value_display, event_type, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border-radius: 3px; /* Slightly smaller radius */
                padding: 3px; /* Reduced padding */
                margin: 2px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2) # Reduced margins
        layout.setSpacing(1) # Reduced spacing
        
        # Event type indicator
        type_label_color = self._get_type_display_color(event_type) # Get specific color for type text
        type_label = QLabel(event_type.upper())
        type_label.setStyleSheet(f"color: {type_label_color}; font-weight: bold; font-size: 8px;") # Smaller font, specific color
        layout.addWidget(type_label)
        
        # Main Title (e.g., Goal Name, Habit Name)
        title_label = QLabel(title)
        # Ensure title_label text is black by default or set explicitly
        title_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #000000;") # Smaller font, black color
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Secondary Info (e.g., Check-in progress, Habit result)
        if date_or_value_display: 
            info_label = QLabel(str(date_or_value_display))
            info_label.setStyleSheet("font-size: 9px; color: #000000;") # Smaller font, black color
            info_label.setWordWrap(True)
            layout.addWidget(info_label)

    def _get_type_display_color(self, event_type):
        # Define colors for the TYPE indicator text itself, ensuring contrast against #f0f0f0
        colors = {
            'Goal': '#1E8449',       # Darker Green
            'Check-in': '#2874A6',  # Darker Blue
            'Habit': '#B71C1C',      # Darker Red
            'Sub-goal': '#B9770E',   # Darker Yellow/Orange
            'Note': '#4A235A'       # Dark Purple for Notes
        }
        return colors.get(event_type, '#424242') # Dark Gray default

    def _get_color_for_type(self, event_type):
        # This was for the type label text, let's rename and repurpose or ensure it's distinct
        # For now, let's assume the above method is the primary one for type text color
        # If this was for a background or border, it needs to be used differently.
        # Based on current usage, _get_type_display_color is now the one styling the type label text.
        # This method might be redundant if not used for other styling aspects.
        # For clarity, I'll keep its original intent for now if it was different.
        colors = {
            'Goal': '#2ecc71',
            'Check-in': '#3498db',
            'Habit': '#e74c3c',
            'Sub-goal': '#f1c40f',
            'Note': '#8E44AD'      # Purple for Notes
        }
        return colors.get(event_type, '#95a5a6')

class CalendarView(QWidget):
    def __init__(self, goal_service: GoalService, habit_service: HabitService, dashboard_service: DashboardService):
        super().__init__()
        self.goal_service = goal_service
        self.habit_service = habit_service
        self.dashboard_service = dashboard_service
        self._active_habits_cache = [] 
        
        # Initialize UI elements first
        self.setup_ui() # This creates self.calendar and self.habit_heatmap_selector
        
        # Then populate dynamic UI elements
        self._populate_habit_heatmap_selector()
        
        # Then connect signals
        self.calendar.currentPageChanged.connect(self._update_calendar_date_formats) 
        self.calendar.activated.connect(self._on_calendar_date_activated) 
        if hasattr(self, 'habit_heatmap_selector'): # Check if it exists
            self.habit_heatmap_selector.currentIndexChanged.connect(self._on_habit_heatmap_selection_changed)
        
        # Finally, make the initial call to format the calendar
        self._update_calendar_date_formats() 
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Calendar")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(title)
        
        # View selector
        self.view_selector = QComboBox()
        self.view_selector.addItems(['All Events', 'Goals', 'Check-ins', 'Habits', 'Notes'])
        self.view_selector.currentTextChanged.connect(self.update_calendar)
        header.addWidget(self.view_selector)

        # Habit Heatmap selector
        self.habit_heatmap_label = QLabel("Habit Heatmap:")
        header.addWidget(self.habit_heatmap_label)
        self.habit_heatmap_selector = QComboBox()
        self.habit_heatmap_selector.setMinimumWidth(150)
        header.addWidget(self.habit_heatmap_selector)
        
        layout.addLayout(header)
        
        # Calendar and events container
        content_layout = QHBoxLayout()
        
        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.date_selected)

        # Style the calendar for a light background and black text
        self.calendar.setStyleSheet("""
            QCalendarWidget QWidget { 
                alternate-background-color: #f5f5f5; /* Light gray for alternate rows */
                background-color: #ffffff; /* White background for main cells */
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #000000; /* Black text */
                selection-background-color: #a8d8ff; /* Light blue for selection */
                selection-color: #000000; /* Black text for selection */
            }
            QCalendarWidget QToolButton {
                color: #000000; /* Black text for navigation buttons */
            }
            #qt_calendar_navigationbar {
                background-color: #e0e0e0; /* Light gray for navigation bar */
            }
        """)

        # Set weekend day names and dates to black
        black_text_format = QTextCharFormat()
        black_text_format.setForeground(QColor("black"))
        self.calendar.setWeekdayTextFormat(Qt.Saturday, black_text_format)
        self.calendar.setWeekdayTextFormat(Qt.Sunday, black_text_format)
        
        content_layout.addWidget(self.calendar)
        
        # Events panel
        events_panel = QWidget()
        events_layout = QVBoxLayout(events_panel)
        
        # Events header
        self.events_header = QLabel("Events")
        self.events_header.setStyleSheet("font-size: 18px; font-weight: bold;")
        events_layout.addWidget(self.events_header)
        
        # Events scroll area
        scroll = QScrollArea()
        self.events_container = QWidget()
        self.events_layout = QVBoxLayout(self.events_container)
        scroll.setWidget(self.events_container)
        scroll.setWidgetResizable(True)
        events_layout.addWidget(scroll)
        
        content_layout.addWidget(events_panel)
        layout.addLayout(content_layout)
        
        # Initialize with today's date
        self.date_selected(QDate.currentDate())
        
    def date_selected(self, date):
        self.selected_date = date.toPyDate()
        self.events_header.setText(f"Events for {self.selected_date.strftime('%B %d, %Y')}")
        self.update_events()
        
    def update_events(self):
        self.events_header.setText(f"Events for {self.selected_date.strftime('%B %d, %Y')}")

        # Clear existing events
        while self.events_layout.count():
            child = self.events_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        event_widgets = self._get_events_for_date(self.selected_date) # Now returns widgets

        if event_widgets:
            for widget in event_widgets:
                self.events_layout.addWidget(widget)
        else:
            no_events_label = QLabel("No events for this day.")
            no_events_label.setAlignment(Qt.AlignCenter)
            self.events_layout.addWidget(no_events_label)
        
        self.events_layout.addStretch() # Ensure events are pushed to the top
    
    def _get_events_for_date(self, date: DateObject) -> list:
        events = []
        view_filter = self.view_selector.currentText()

        # Fetch Goals
        if view_filter in ['All Events', 'Goals']:
            goals_on_date = self.goal_service.get_goals_by_target_date(date)
            for goal in goals_on_date:
                events.append(CalendarEventWidget(goal.name, f"Target: {goal.target_date.strftime('%Y-%m-%d')}", 'Goal'))
                # Optionally, fetch and display sub-goals if logic requires it here

        # Fetch Check-ins
        if view_filter in ['All Events', 'Check-ins']:
            check_ins_on_date = self.goal_service.get_check_ins_for_date_with_goal(date)
            for check_in in check_ins_on_date:
                events.append(CalendarEventWidget(
                    f"Check-in for: {check_in.goal.name}", 
                    f"Progress: {check_in.progress_percentage}%\n{check_in.reflection[:50] + '...' if check_in.reflection and len(check_in.reflection) > 50 else check_in.reflection or ''}",
                    'Check-in'
                ))

        # Fetch Habit Entries
        if view_filter in ['All Events', 'Habits']:
            habit_entries_on_date = self.habit_service.get_habit_entries_for_date_with_habit(date)
            for entry in habit_entries_on_date:
                status = "Completed" if entry.completed else "Not Completed"
                if entry.habit.completion_type == CompletionType.QUANTITATIVE and entry.value is not None:
                    status += f": {entry.value} {entry.habit.unit or ''}"
                elif entry.habit.completion_type == CompletionType.DURATION and entry.value is not None:
                    status += f": {entry.value} mins"
                events.append(CalendarEventWidget(entry.habit.name, status, 'Habit'))
        
        # Fetch Dated Notes
        if view_filter in ['All Events', 'Notes']: # Assuming 'Notes' could be an option in view_selector
                                                # Or just always show if 'All Events' or if no specific filter hides them
            notes_on_date = self.dashboard_service.get_notes_for_date(date)
            for note in notes_on_date:
                snippet = (note.content[:75] + '...') if len(note.content) > 75 else note.content
                event_title = f"Note @ {note.created_at.strftime('%H:%M:%S')}"
                events.append(CalendarEventWidget(event_title, snippet.splitlines()[0] if snippet else "", 'Note'))

        return events

    def update_calendar(self):
        self.update_events()
        self._update_calendar_date_formats()

    def _populate_habit_heatmap_selector(self):
        self.habit_heatmap_selector.blockSignals(True)
        self.habit_heatmap_selector.clear()
        self.habit_heatmap_selector.addItem("General Event View", None) # Option to clear heatmap
        # Ensure _active_habits_cache is populated if it can be empty initially
        if not self._active_habits_cache: 
            self._active_habits_cache = self.habit_service.get_active_habits()
        for habit in self._active_habits_cache:
            self.habit_heatmap_selector.addItem(habit.name, habit.id)
        self.habit_heatmap_selector.blockSignals(False)

    def _on_habit_heatmap_selection_changed(self, index):
        self._update_calendar_date_formats()

    def _clear_calendar_formats(self):
        """Clears any custom formatting for all dates."""
        # Creating an empty QTextCharFormat resets the format for a date.
        # We need to do this for all dates in the currently visible month grid.
        # A simpler way if QCalendarWidget doesn't have a direct "clear all formats" method
        # is to iterate through the dates of the displayed month.
        year = self.calendar.yearShown()
        month = self.calendar.monthShown()
        num_days = calendar.monthrange(year, month)[1]
        default_format = QTextCharFormat() # An empty format
        for day in range(1, num_days + 1):
            date_to_clear = QDate(year, month, day)
            self.calendar.setDateTextFormat(date_to_clear, default_format)

    def _update_calendar_date_formats(self):
        """Updates the text formatting of dates in the calendar grid based on events."""
        self._clear_calendar_formats() 

        year = self.calendar.yearShown()
        month = self.calendar.monthShown()
        
        first_day_of_month = DateObject(year, month, 1)
        num_days_in_month = calendar.monthrange(year, month)[1]
        last_day_of_month = DateObject(year, month, num_days_in_month)

        selected_heatmap_habit_id = self.habit_heatmap_selector.currentData()

        if selected_heatmap_habit_id is not None:
            # --- Habit Heatmap Mode ---
            try:
                habit_entries = self.habit_service.get_all_entries_for_habit_in_period(
                    selected_heatmap_habit_id, first_day_of_month, last_day_of_month
                )
                entries_by_date = {entry.completion_date.date(): entry for entry in habit_entries}
                
                habit_completed_format = QTextCharFormat()
                habit_completed_format.setBackground(QColor("#a9dfbf")) # Green for completed
                habit_completed_format.setToolTip("Habit Completed")

                habit_missed_format = QTextCharFormat()
                habit_missed_format.setBackground(QColor("#f5b7b1")) # Light red for missed/not completed
                habit_missed_format.setToolTip("Habit Not Completed")
                
                # To identify streaks, we'd need more logic here if we want specific formatting
                # For now, just color completed/missed based on daily entry

                for day in range(1, num_days_in_month + 1):
                    current_date_obj = DateObject(year, month, day)
                    q_date = QDate(year, month, day)
                    entry = entries_by_date.get(current_date_obj)
                    if entry:
                        if entry.completed:
                            self.calendar.setDateTextFormat(q_date, habit_completed_format)
                        else:
                            self.calendar.setDateTextFormat(q_date, habit_missed_format)
                    # else: no entry for this day for the selected habit, so no specific habit format

            except Exception as e:
                logger.error(f"Error fetching habit entries for heatmap: {e}")
        else:
            # --- General Event Markers Mode ---
            goal_target_dates = set()
            checkin_dates = set()
            habit_entry_dates = set() # General habit entries, not specific heatmap

            event_filter = self.view_selector.currentText()

            try:
                if event_filter in ['All Events', 'Goals']:
                    goal_target_dates = self.goal_service.get_goal_target_dates_in_period(first_day_of_month, last_day_of_month)
                if event_filter in ['All Events', 'Check-ins']:
                    checkin_dates = self.goal_service.get_checkin_dates_in_period(first_day_of_month, last_day_of_month)
                if event_filter in ['All Events', 'Habits']: # This fetches general habit completion markers
                    habit_entry_dates = self.habit_service.get_habit_entry_dates_in_period(first_day_of_month, last_day_of_month)
            except Exception as e:
                logger.error(f"Error fetching event dates for calendar formats: {e}")
                return

            goal_format = QTextCharFormat()
            goal_format.setBackground(QColor("#d4efdf")) 
            goal_format.setToolTip("Goal target date")

            general_habit_format = QTextCharFormat() # Renamed to avoid confusion
            general_habit_format.setBackground(QColor("#fdebd0")) 
            general_habit_format.setToolTip("Habit logged (general)")

            checkin_format = QTextCharFormat()
            checkin_format.setBackground(QColor("#d6eaf8")) 
            checkin_format.setToolTip("Check-in made")

            multiple_events_format = QTextCharFormat()
            multiple_events_format.setFontWeight(QFont.Bold) 
            multiple_events_format.setToolTip("Multiple events")

            for day in range(1, num_days_in_month + 1):
                current_date_obj = DateObject(year, month, day)
                q_date = QDate(year, month, day)

                has_goal = current_date_obj in goal_target_dates
                # Use general habit_entry_dates for non-heatmap mode
                has_general_habit = current_date_obj in habit_entry_dates 
                has_checkin = current_date_obj in checkin_dates

                event_types_on_date = sum([has_goal, has_general_habit, has_checkin])

                if event_types_on_date > 1:
                    self.calendar.setDateTextFormat(q_date, multiple_events_format)
                elif has_goal:
                    self.calendar.setDateTextFormat(q_date, goal_format)
                elif has_general_habit: # Use the general habit format
                    self.calendar.setDateTextFormat(q_date, general_habit_format)
                elif has_checkin:
                    self.calendar.setDateTextFormat(q_date, checkin_format)

    def _on_calendar_date_activated(self, q_date: QDate):
        """Handle double-click on a calendar date."""
        selected_py_date = q_date.toPyDate()
        
        actions = {"Add New Goal": lambda: self._quick_add_goal(selected_py_date),
                   "Record Habit Entry": lambda: self._quick_record_habit_entry(selected_py_date)
                   # Add more actions here later
                  }
        
        item, ok = QInputDialog.getItem(self, "Quick Add", 
                                        f"Selected Date: {selected_py_date.strftime('%Y-%m-%d')}\nWhat would you like to do?", 
                                        list(actions.keys()), 0, False)
        
        if ok and item:
            action_func = actions.get(item)
            if action_func:
                action_func()

    def _fetch_all_values_for_dialog(self) -> List[Value]:
        # This method is similar to one in GoalsView, adapted for CalendarView's service access
        # Ensure ValueService is accessible, e.g. self.value_service if passed in __init__
        # For now, assuming goal_service might have a way or it needs a new service instance.
        # This example assumes it's okay to create a ValueService instance if not available.
        # Proper dependency injection would be better.
        # For this fix, let's assume self.goal_service can access ValueService or we create it.
        # This part is not directly related to the category removal from GoalDialog.
        # The original code for this method was:
        # try:
        #     # This would require having access to a ValueService instance.
        #     # If GoalService is expected to provide this, it needs a method.
        #     # For now, let's assume this would be handled by a ValueService if available.
        #     # This method wasn't in the provided snippet, so I'm working from the outline.
        #     # return self.value_service.get_all_values() # Ideal
        #     logger.warning("_fetch_all_values_for_dialog in CalendarView needs ValueService access.")
        #     return [] # Placeholder
        # except Exception as e:
        #     logger.error(f"Error fetching values for GoalDialog from CalendarView: {e}")
        #     QMessageBox.warning(self, "Error", "Could not fetch values for the dialog.")
        #     return []
        # Based on the context, this method IS used by _quick_add_goal.
        # And it's similar to GoalsView. Let's assume ValueService is not directly available.
        # This method might need a ValueService passed to CalendarView's init.
        # For now, to ensure it runs, I will return an empty list.
        # If ValueService is available as self.value_service, then use it.
        # For now, to ensure it runs if called, returning empty. This is a placeholder.
        # Ideally, CalendarView's __init__ would take ValueService.
        logger.warning("CalendarView._fetch_all_values_for_dialog: ValueService not available. Returning empty list.")
        return []

    def _quick_add_goal(self, selected_date: datetime.date):
        all_values = self._fetch_all_values_for_dialog() 
        # Categories are no longer needed for GoalDialog
        # all_categories = self._fetch_all_categories_for_dialog()

        # Fetch eligible parent goals (similar to GoalsView)
        # This requires self.goal_service to have get_all_goals_for_parent_selection
        eligible_parents = []
        try:
            eligible_parents = self.goal_service.get_all_goals_for_parent_selection()
        except Exception as e:
            logger.error(f"Error fetching parent goals for GoalDialog from CalendarView: {e}")
            QMessageBox.warning(self, "Error", "Could not fetch parent goals for the dialog.")

        all_active_habits = []
        try:
            all_active_habits = self.habit_service.get_active_habits()
        except Exception as e:
             logger.error(f"Error fetching active habits for GoalDialog from CalendarView: {e}")
             QMessageBox.warning(self, "Error", "Could not fetch active habits for the dialog.")

        dialog = GoalDialog(
            parent=self,
            all_values=all_values,
            # all_categories=all_categories, # Removed
            all_active_habits=all_active_habits,
            eligible_parent_goals=eligible_parents, # Ensure this method exists in GoalService
            target_date_override=selected_date
        )
        if dialog.exec_() == QDialog.Accepted:
            goal_data = dialog.get_goal_form_data()
            self.goal_service.create_goal(
                name=goal_data['name'],
                description=goal_data['description'],
                target_date=goal_data['target_date'], # This will come from the dialog
                status=goal_data['status'],
                # category_id=goal_data['category_id'], # Removed: Category no longer part of Goal
                parent_id=goal_data['parent_id'], # Ensure parent_id is in get_goal_form_data()
                linked_value_ids=goal_data['linked_value_ids'],
                linked_habit_ids=goal_data['linked_habit_ids']
            )
            self.update_events() # Refresh side panel list
            self._update_calendar_date_formats() # Refresh calendar cell markers
            QMessageBox.information(self, "Success", "Goal added successfully!")

    def _quick_record_habit_entry(self, selected_date: datetime.date):
        try:
            active_habits = self.habit_service.get_active_habits()
            if not active_habits:
                QMessageBox.information(self, "No Active Habits", "There are no active habits to log an entry for.")
                return

            habit_names = [h.name for h in active_habits]
            habit_name, ok = QInputDialog.getItem(self, "Select Habit", 
                                                "Which habit do you want to log?", 
                                                habit_names, 0, False)
            
            if ok and habit_name:
                selected_habit_obj = next((h for h in active_habits if h.name == habit_name), None)
                if not selected_habit_obj:
                    QMessageBox.critical(self, "Error", "Selected habit not found.") # Should not happen
                    return

                dialog = QuickHabitEntryDialog(selected_habit_obj, selected_date, self)
                if dialog.exec_() == QDialog.Accepted:
                    entry_data = dialog.get_entry_data()
                    self.habit_service.record_habit_entry(
                        habit_id=selected_habit_obj.id,
                        completed=entry_data['completed'],
                        value=entry_data['value'],
                        notes=entry_data['notes'],
                        completion_date_override=datetime.combine(selected_date, datetime.now().time()) # Use selected date, current time
                    )
                    self.update_events() # Refresh side panel list
                    self._update_calendar_date_formats() # Refresh calendar cell markers
                    QMessageBox.information(self, "Success", f"Entry for '{selected_habit_obj.name}' recorded.")
        except Exception as e:
            logger.error(f"Error during quick record habit entry: {e}")
            QMessageBox.critical(self, "Error", f"Failed to quick record habit entry: {str(e)}") 