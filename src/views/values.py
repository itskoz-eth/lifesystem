from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem, QDialog, QFormLayout, 
                             QLineEdit, QTextEdit, QDialogButtonBox, QMessageBox,
                             QColorDialog, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from ..models.value import Value
from ..models.category import Category
from ..services.value_service import ValueService
import logging
import random

logger = logging.getLogger(__name__)

class ValueDialog(QDialog):
    def __init__(self, parent=None, value=None):
        super().__init__(parent)
        self.value = value
        self.setWindowTitle("Edit Value" if value else "Add New Value")
        self.setup_ui()
        if value:
            self.load_value_data()
    
    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        layout.addRow("&Name:", self.name_input)

        self.description_input = QTextEdit()
        layout.addRow("&Description:", self.description_input)
        
        self.color_button = QPushButton("Choose Display Color")
        self.color_button.clicked.connect(self.choose_color)
        
        h = random.randint(0, 359)
        s = random.randint(25, 75)
        l = random.randint(75, 90)
        self.current_display_color = self.hsl_to_qcolor(h, s, l)
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

        self.setLayout(layout)

        QWidget.setTabOrder(self.name_input, self.description_input)
        QWidget.setTabOrder(self.description_input, self.color_button)
    
    def hsl_to_qcolor(self, h, s, l):
        """Convert HSL to QColor (h: 0-359, s: 0-100, l: 0-100)"""
        h = h / 360.0
        s = s / 100.0
        l = l / 100.0
        
        if s == 0:
            r = g = b = l
        else:
            def hue_to_rgb(p, q, t):
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1/6: return p + (q - p) * 6 * t
                if t < 1/2: return q
                if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                return p
            
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1/3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1/3)
        
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def choose_color(self):
        color = QColorDialog.getColor(self.current_display_color, self, "Choose Value Display Color")
        if color.isValid():
            self.current_display_color = color
    
    def load_value_data(self):
        self.name_input.setText(self.value.name)
        self.description_input.setText(self.value.description or "")
    
    def get_value_data(self):
        return {
            'name': self.name_input.text(),
            'description': self.description_input.toPlainText(),
        }

class ValuesView(QWidget):
    def __init__(self, value_service: ValueService):
        super().__init__()
        self.value_service = value_service
        self.value_display_colors = {}
        self.setup_ui()
        self.load_values()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        title = QLabel("Core Values")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        add_button = QPushButton("Add New Value")
        add_button.clicked.connect(self.show_add_value_dialog)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(add_button)
        layout.addLayout(header)
        
        self.values_list = QListWidget()
        self.values_list.setAlternatingRowColors(True)
        self.values_list.itemDoubleClicked.connect(self.edit_selected_value)
        layout.addWidget(self.values_list)
        
        button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Edit Selected")
        self.delete_button = QPushButton("Delete Selected")
        self.edit_button.clicked.connect(self.edit_selected_value)
        self.delete_button.clicked.connect(self.delete_selected_value)
        button_layout.addStretch()
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)
    
    def load_values(self):
        try:
            values = self.value_service.get_all_values()
            self.values_list.clear()
            self.value_display_colors.clear()

            for value in values:
                if value.id not in self.value_display_colors:
                    h = random.randint(0, 359)
                    s = random.randint(25, 75)
                    l = random.randint(75, 90)
                    self.value_display_colors[value.id] = self._hsl_to_qcolor(h, s, l)
                
                item_text = f"{value.name}"
                if value.description:
                    first_line_desc = value.description.split('\n')[0]
                    item_text += f"\n  └ {first_line_desc[:80]}{'...' if len(first_line_desc) > 80 else ''}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, value.id)
                
                display_color = self.value_display_colors[value.id]
                item.setBackground(display_color)
                item.setForeground(QColor('white' if display_color.lightness() < 128 else 'black'))
                
                tooltip_text = f"Name: {value.name}\nDescription: {value.description or 'None'}"
                item.setToolTip(tooltip_text)
                
                self.values_list.addItem(item)
                
        except Exception as e:
            logger.error(f"Error loading values: {str(e)}")
            QMessageBox.critical(self, "Error", f"Could not load values: {str(e)}")

    def _hsl_to_qcolor(self, h, s, l):
        h = h / 360.0
        s = s / 100.0
        l = l / 100.0
        
        if s == 0:
            r = g = b = l
        else:
            def hue_to_rgb(p, q, t):
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1/6: return p + (q - p) * 6 * t
                if t < 1/2: return q
                if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                return p
            
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1/3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1/3)
        
        return QColor(int(r * 255), int(g * 255), int(b * 255))

    def show_add_value_dialog(self):
        dialog = ValueDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            value_data = dialog.get_value_data()
            if not value_data['name'].strip():
                QMessageBox.warning(self, "Input Error", "Value name cannot be empty.")
                return

            new_value = self.value_service.create_value(
                name=value_data['name'],
                description=value_data['description']
            )
            if new_value:
                self.load_values()
                QMessageBox.information(self, "Success", "Value added successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to add value.")
    
    def edit_selected_value(self):
        selected_items = self.values_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a value to edit.")
            return
        
        value_id = selected_items[0].data(Qt.UserRole)
        value_to_edit = self.value_service.get_value(value_id)

        if not value_to_edit:
            QMessageBox.critical(self, "Error", "Selected value not found or could not be loaded.")
            self.load_values()
            return
            
        dialog = ValueDialog(self, value=value_to_edit)
        
        if dialog.exec_() == QDialog.Accepted:
            value_data = dialog.get_value_data()
            if not value_data['name'].strip():
                QMessageBox.warning(self, "Input Error", "Value name cannot be empty.")
                return

            updated_value = self.value_service.update_value(
                value_id=value_to_edit.id,
                name=value_data['name'],
                description=value_data['description']
            )
            if updated_value:
                self.load_values()
                QMessageBox.information(self, "Success", "Value updated successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to update value.")
    
    def delete_selected_value(self):
        selected_items = self.values_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a value to delete.")
            return
            
        value_id = selected_items[0].data(Qt.UserRole)
        value_to_delete = self.value_service.get_value(value_id)

        if not value_to_delete:
             QMessageBox.critical(self, "Error", "Selected value not found. It may have already been deleted.")
             self.load_values()
             return

        reply = QMessageBox.question(self, 'Confirm Delete', 
                                     f"Are you sure you want to delete the value: {value_to_delete.name}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.value_service.delete_value(value_id):
                self.load_values()
                QMessageBox.information(self, "Success", "Value deleted successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete value.") 