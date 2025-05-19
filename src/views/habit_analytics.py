from datetime import datetime, timedelta
from typing import List, Dict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates # For better date formatting
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QComboBox, QFrame)
from PyQt5.QtCore import Qt
from ..models.enhanced_models import Habit, CompletionType # Import CompletionType
from ..services.habit_service import HabitService

class HabitAnalyticsView(QWidget):
    """View for displaying habit analytics and visualizations."""
    def __init__(self, habit_service: HabitService, parent=None):
        super().__init__(parent)
        self.habit_service = habit_service
        self.setup_ui()
        self.load_habits()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Habit Analytics")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)

        # Habit selector
        self.habit_combo = QComboBox()
        self.habit_combo.currentIndexChanged.connect(self.on_habit_selected)
        header_layout.addWidget(self.habit_combo)

        layout.addLayout(header_layout)

        # Stats frame
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)

        # Current streak
        self.streak_label = QLabel("Current Streak: 0")
        self.streak_label.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(self.streak_label)

        # Completion rate
        self.rate_label = QLabel("Completion Rate: 0%")
        self.rate_label.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(self.rate_label)

        layout.addWidget(stats_frame)

        # Matplotlib figure
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def load_habits(self):
        """Load habits into the combo box."""
        habits = self.habit_service.get_active_habits()
        self.habit_combo.clear()
        for habit in habits:
            self.habit_combo.addItem(habit.name, habit.id)

        if habits:
            self.on_habit_selected(0)

    def on_habit_selected(self, index):
        if index < 0:
            self.figure.clear()
            self.canvas.draw()
            self.streak_label.setText("Current Streak: N/A")
            self.rate_label.setText("Completion Rate: N/A")
            return

        habit_id = self.habit_combo.currentData()
        if habit_id is None: # Should not happen if combo is populated
            self.figure.clear()
            self.canvas.draw()
            return
            
        habit = self.habit_service.get_habit(habit_id)
        if not habit:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "Habit not found.", ha='center', va='center')
            self.canvas.draw()
            return

        self.update_stats(habit)
        self.update_charts(habit)

    def update_stats(self, habit: Habit):
        streak = self.habit_service.get_current_streak(habit.id)
        completion_rate = self.habit_service.get_completion_rate(habit.id)
        self.streak_label.setText(f"Current Streak: {streak} days")
        self.rate_label.setText(f"Completion Rate (30d): {completion_rate:.1f}%")

    def update_charts(self, habit: Habit):
        self.figure.clear()
        self.figure.patch.set_facecolor('#ECE9D8')
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#F5F5F5')

        days_to_show = 30
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_to_show)
        entries = self.habit_service.get_habit_entries(habit.id, start_date, end_date)
        entries.sort(key=lambda e: e.completion_date) # Ensure chronological order for plotting

        dates = [entry.completion_date.date() for entry in entries]

        if not entries:
            ax.text(0.5, 0.5, f"No data for '{habit.name}' in the last {days_to_show} days", ha='center', va='center')
        elif habit.completion_type == CompletionType.BINARY:
            self._plot_binary_completion_trend(ax, habit, entries, dates)
        elif habit.completion_type in [CompletionType.QUANTITATIVE, CompletionType.DURATION]:
            self._plot_quantitative_trend(ax, habit, entries, dates)
        
        # Common styling
        ax.grid(True, linestyle='--', alpha=0.6, color='#D0D0D0')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#B0B0B0')
        ax.spines['bottom'].set_color('#B0B0B0')
        ax.tick_params(colors='#4A4A4A', labelsize=9)
        if dates:
             plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
        try:
            self.figure.tight_layout(pad=1.5)
        except Exception: pass
        self.canvas.draw()

    def _plot_binary_completion_trend(self, ax, habit: Habit, entries: List, dates: List):
        if not entries:
            ax.text(0.5, 0.5, f"No completion data for '{habit.name}' in this period", ha='center', va='center')
            ax.set_title(f"'{habit.name}' - Completion Log", color='#333333')
            ax.set_xlabel("Date", color='#4A4A4A')
            ax.set_ylabel("Cumulative Completions", color='#4A4A4A')
            return

        # Ensure entries are sorted by date for cumulative sum
        sorted_entries = sorted(entries, key=lambda e: e.completion_date)
        plot_dates = [entry.completion_date.date() for entry in sorted_entries]
        
        cumulative_completions = []
        current_completions = 0
        for entry in sorted_entries:
            if entry.completed:
                current_completions += 1
            cumulative_completions.append(current_completions)
        
        ax.plot(plot_dates, cumulative_completions, '-', color='#27AE60', linewidth=2, label='Cumulative Completions')
        ax.fill_between(plot_dates, cumulative_completions, color='#27AE60', alpha=0.2)

        ax.set_title(f"'{habit.name}' - Cumulative Completion Log", color='#333333', fontsize=10)
        ax.set_xlabel("Date", color='#4A4A4A', fontsize=9)
        ax.set_ylabel("Total Days Completed", color='#27AE60', fontsize=9)
        ax.tick_params(axis='y', labelcolor='#27AE60', labelsize=8)
        
        if plot_dates:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            ax.set_xlim(min(plot_dates) - timedelta(days=1), max(plot_dates) + timedelta(days=1))
        
        ax.legend(loc='upper left', fontsize=8)

    def _plot_quantitative_trend(self, ax, habit: Habit, entries: List, dates: List):
        if not entries: # Handle case with no entries for the period
            ax.text(0.5, 0.5, f"No data for '{habit.name}' in this period", ha='center', va='center')
            ax.set_title(f"'{habit.name}' - Value Logged Over Time", color='#333333')
            ax.set_xlabel("Date", color='#4A4A4A')
            ax.set_ylabel(f"Value{(' (' + habit.unit + ')') if habit.unit else ''}", color='#4A4A4A')
            return

        values = [entry.value if entry.completed and entry.value is not None else 0 for entry in entries]
        # Ensure dates align with values for plotting, especially if some days have no entries
        # For simplicity, we assume entries are sorted and cover the intended date range for now.
        # More robust approach might create a full date range and map values to it.
        
        # Bar chart for daily values (left Y-axis)
        ax.bar(dates, values, color='#3875D7', width=0.8, label='Daily Value')
        unit = f" ({habit.unit})" if habit.unit else ""
        ax.set_title(f"'{habit.name}' - Daily & Cumulative Value{unit}", color='#333333', fontsize=10)
        ax.set_xlabel("Date", color='#4A4A4A', fontsize=9)
        ax.set_ylabel(f"Daily Value{unit}", color='#3875D7', fontsize=9)
        ax.tick_params(axis='y', labelcolor='#3875D7', labelsize=8)
        ax.grid(True, linestyle=':', linewidth=0.7, color='#BBBBBB', alpha=0.7)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        if dates:
            ax.set_xlim(min(dates) - timedelta(days=1), max(dates) + timedelta(days=1))

        # Accumulation line (right Y-axis)
        cumulative_values = []
        current_sum = 0
        for val in values:
            current_sum += val
            cumulative_values.append(current_sum)
        
        ax2 = ax.twinx() # Create a second y-axis sharing the same x-axis
        ax2.plot(dates, cumulative_values, color='#27AE60', linestyle='--', marker='.', markersize=3, linewidth=1.5, label='Cumulative Value')
        ax2.set_ylabel(f"Cumulative Value{unit}", color='#27AE60', fontsize=9)
        ax2.tick_params(axis='y', labelcolor='#27AE60', labelsize=8)
        ax2.spines['top'].set_visible(False) # Keep common styling consistent

        # Add legends
        # For combined legends from two axes: https://matplotlib.org/stable/gallery/subplots_axes_and_figures/two_scales.html
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper left', fontsize=8) 