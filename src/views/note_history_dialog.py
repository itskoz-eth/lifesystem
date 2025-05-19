from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QTextBrowser, 
                             QPushButton, QListWidgetItem, QMessageBox, QLabel, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from ..services.dashboard_service import DashboardService
from ..models.whiteboard_note import DatedNote # DatedNote model
from typing import List

class NoteHistoryDialog(QDialog):
    def __init__(self, dashboard_service: DashboardService, parent=None):
        super().__init__(parent)
        self.dashboard_service = dashboard_service
        self.notes_cache: List[DatedNote] = [] # To hold the currently loaded notes

        self.setWindowTitle("View Past Notes")
        self.setMinimumSize(600, 400)

        main_layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("Browse and manage your saved notes.")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(header_label)

        # Main content area (list on left, text browser on right)
        content_layout = QHBoxLayout()
        
        # Left side: List of notes
        list_area_layout = QVBoxLayout()
        list_label = QLabel("Saved Notes:")
        self.notes_list_widget = QListWidget()
        self.notes_list_widget.itemSelectionChanged.connect(self.display_selected_note)
        list_area_layout.addWidget(list_label)
        list_area_layout.addWidget(self.notes_list_widget)
        
        content_layout.addLayout(list_area_layout, 1) # Proportion 1

        # Right side: Display full note
        display_area_layout = QVBoxLayout()
        display_label = QLabel("Note Content:")
        self.note_content_browser = QTextBrowser()
        display_area_layout.addWidget(display_label)
        display_area_layout.addWidget(self.note_content_browser)
        
        content_layout.addLayout(display_area_layout, 2) # Proportion 2 (wider)

        main_layout.addLayout(content_layout)

        # Bottom buttons
        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Delete Selected Note")
        self.delete_button.clicked.connect(self.delete_selected_note)
        self.delete_button.setEnabled(False) # Disabled until a note is selected

        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.load_notes)
        
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(QPushButton("Close", clicked=self.accept))
        
        main_layout.addLayout(button_layout)

        self.load_notes()

    def load_notes(self):
        self.notes_list_widget.clear()
        self.note_content_browser.clear()
        self.delete_button.setEnabled(False)
        
        self.notes_cache = self.dashboard_service.get_all_notes() # Fetches all, ordered by date desc
        
        if not self.notes_cache:
            self.notes_list_widget.addItem("No notes found.")
            return

        for note in self.notes_cache:
            # Display date and a snippet of content
            # note.note_date is a datetime.date object
            # note.created_at is a datetime.datetime object for more precise sorting if needed
            snippet = (note.content[:75] + '...') if len(note.content) > 75 else note.content
            item_text = f"{note.note_date.strftime('%Y-%m-%d')} ({note.created_at.strftime('%H:%M:%S')}): {snippet.splitlines()[0]}"
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.UserRole, note.id) # Store note ID with the item
            self.notes_list_widget.addItem(list_item)

    def display_selected_note(self):
        selected_items = self.notes_list_widget.selectedItems()
        if not selected_items:
            self.note_content_browser.clear()
            self.delete_button.setEnabled(False)
            return

        selected_item = selected_items[0]
        note_id = selected_item.data(Qt.UserRole)
        
        selected_note = next((n for n in self.notes_cache if n.id == note_id), None)
        
        if selected_note:
            self.note_content_browser.setText(f"Date: {selected_note.note_date.strftime('%Y-%m-%d %H:%M:%S')}\n\n{selected_note.content}")
            self.delete_button.setEnabled(True)
        else:
            self.note_content_browser.setText("Could not load note content.")
            self.delete_button.setEnabled(False)

    def delete_selected_note(self):
        selected_items = self.notes_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Note Selected", "Please select a note to delete.")
            return

        selected_item = selected_items[0]
        note_id = selected_item.data(Qt.UserRole)
        note_to_delete = next((n for n in self.notes_cache if n.id == note_id), None)

        if not note_to_delete:
             QMessageBox.critical(self, "Error", "Selected note not found in cache. Please refresh.")
             return

        confirm_msg = f"Are you sure you want to delete the note from {note_to_delete.note_date.strftime('%Y-%m-%d')}?"
        reply = QMessageBox.question(self, 'Confirm Deletion', confirm_msg, 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.dashboard_service.delete_note(note_id):
                QMessageBox.information(self, "Success", "Note deleted successfully.")
                self.load_notes() # Refresh the list
            else:
                QMessageBox.critical(self, "Error", "Failed to delete the note from the database.")
 