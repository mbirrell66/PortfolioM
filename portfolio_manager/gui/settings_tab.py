"""
Settings tab for Portfolio Manager
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLabel, QComboBox, QPushButton, QCheckBox,
                              QSpinBox, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt


_TAB_SS = """
    QWidget { background-color: #0F1117; }
    QTabWidget::pane {
        background-color: #0F1117;
        border: 1px solid #222844;
        border-radius: 8px;
        margin-top: -1px;
    }
    QTabBar::tab {
        background-color: #191D2E; color: #7488B8;
        padding: 10px 20px; font-size: 13px; font-weight: 500;
        border: 1px solid #222844; border-bottom: none;
        border-top-left-radius: 6px; border-top-right-radius: 6px;
        margin-right: 4px;
    }
    QTabBar::tab:selected { background-color: #0F1117; color: #5295FF; font-weight: 600; }
    QTabBar::tab:hover { color: #5295FF; }
    QLabel { color: #7488B8; font-size: 13px; }
    QGroupBox {
        color: #7488B8; font-size: 12px; font-weight: 600;
        border: 1px solid #222844; border-radius: 6px;
        margin-top: 8px; padding-top: 8px;
    }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
    QLineEdit, QDateEdit, QDoubleSpinBox, QSpinBox, QComboBox {
        background-color: #191D2E; color: #DDE8FF;
        border: 1px solid #222844; border-radius: 6px;
        padding: 6px 10px; font-size: 13px;
    }
    QLineEdit:focus, QDateEdit:focus, QComboBox:focus,
    QDoubleSpinBox:focus, QSpinBox:focus { border-color: #5295FF; }
    QComboBox::drop-down, QDateEdit::drop-down,
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
    QSpinBox::up-button, QSpinBox::down-button { background-color: #222844; border: none; }
    QComboBox QAbstractItemView {
        background-color: #191D2E; color: #DDE8FF; border: 1px solid #222844;
        selection-background-color: rgba(74, 158, 255, 0.25);
    }
    QCheckBox { color: #DDE8FF; font-size: 13px; }
    QCheckBox::indicator {
        width: 16px; height: 16px;
        border: 1px solid #222844; border-radius: 3px; background-color: #191D2E;
    }
    QCheckBox::indicator:checked { background-color: #5295FF; border-color: #5295FF; }
    QPushButton {
        background-color: #5295FF; color: #0F1117; border: none;
        border-radius: 6px; padding: 8px 20px; font-size: 13px;
        font-weight: 600; min-width: 80px;
    }
    QPushButton:hover { background-color: #4080EE; }
    QPushButton:pressed { background-color: #327AE0; }
"""


class SettingsTab(QWidget):
    """Settings tab for configuring Portfolio Manager."""

    def __init__(self):
        """Initialize settings tab."""
        super().__init__()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        self.setStyleSheet(_TAB_SS)
        
        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QFormLayout(general_group)
        
        self.auto_refresh_checkbox = QCheckBox("Auto-refresh prices on startup")
        self.auto_refresh_checkbox.setChecked(True)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "System"])
        self.theme_combo.setCurrentText("Dark")
        
        self.data_refresh_interval_spin = QSpinBox()
        self.data_refresh_interval_spin.setRange(1, 60)
        self.data_refresh_interval_spin.setValue(5)
        self.data_refresh_interval_spin.setSuffix(" minutes")
        
        general_layout.addRow("Auto-refresh prices:", self.auto_refresh_checkbox)
        general_layout.addRow("Theme:", self.theme_combo)
        general_layout.addRow("Data refresh interval:", self.data_refresh_interval_spin)
        
        layout.addWidget(general_group)
        
        # Market data settings
        market_group = QGroupBox("Market Data Settings")
        market_layout = QFormLayout(market_group)
        
        self.data_source_combo = QComboBox()
        self.data_source_combo.addItems(["Yahoo Finance", "Alpha Vantage", "IEX Cloud"])
        self.data_source_combo.setCurrentText("Yahoo Finance")
        
        self.cache_enabled_checkbox = QCheckBox("Enable data caching")
        self.cache_enabled_checkbox.setChecked(True)
        
        market_layout.addRow("Data source:", self.data_source_combo)
        market_layout.addRow("Cache enabled:", self.cache_enabled_checkbox)
        
        layout.addWidget(market_group)
        
        # Portfolio settings
        portfolio_group = QGroupBox("Portfolio Settings")
        portfolio_layout = QFormLayout(portfolio_group)
        
        self.default_currency_combo = QComboBox()
        self.default_currency_combo.addItems(["USD", "EUR", "GBP", "CAD", "AUD"])
        self.default_currency_combo.setCurrentText("USD")
        
        self.show_zero_positions_checkbox = QCheckBox("Show positions with zero shares")
        self.show_zero_positions_checkbox.setChecked(False)
        
        portfolio_layout.addRow("Default currency:", self.default_currency_combo)
        portfolio_layout.addRow("Show zero positions:", self.show_zero_positions_checkbox)
        
        layout.addWidget(portfolio_group)
        
        # Database management (backup / restore)
        database_group = QGroupBox("Database Management")
        database_layout = QVBoxLayout(database_group)

        db_info_label = QLabel(
            "Back up your portfolio database to a file, or restore it from a "
            "previously saved backup."
        )
        db_info_label.setWordWrap(True)
        database_layout.addWidget(db_info_label)

        db_button_layout = QHBoxLayout()
        backup_btn = QPushButton("Backup Database...")
        backup_btn.clicked.connect(self.backup_database)
        restore_btn = QPushButton("Restore Database...")
        restore_btn.clicked.connect(self.restore_database)
        db_button_layout.addWidget(backup_btn)
        db_button_layout.addWidget(restore_btn)
        db_button_layout.addStretch()
        database_layout.addLayout(db_button_layout)

        layout.addWidget(database_group)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)

        restore_btn = QPushButton("Restore Saved Settings")
        restore_btn.clicked.connect(self.restore_settings)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(restore_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: green;")
        layout.addWidget(self.status_label)
        
        # Set layout spacing
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
    
    def load_settings(self):
        """Load saved settings from file (silent; called on startup)."""
        try:
            self._apply_saved_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")

    def _apply_saved_settings(self):
        """Apply settings from config/settings.json to the form widgets.

        Returns True if a settings file was found and applied, False if no
        settings file exists yet. Raises on read/parse errors.
        """
        import json
        import os

        settings_path = "config/settings.json"
        if not os.path.exists(settings_path):
            return False

        with open(settings_path, 'r') as f:
            settings = json.load(f)

        if 'auto_refresh' in settings:
            self.auto_refresh_checkbox.setChecked(settings['auto_refresh'])
        if 'theme' in settings:
            self.theme_combo.setCurrentText(settings['theme'])
        if 'refresh_interval' in settings:
            self.data_refresh_interval_spin.setValue(settings['refresh_interval'])
        if 'data_source' in settings:
            self.data_source_combo.setCurrentText(settings['data_source'])
        if 'cache_enabled' in settings:
            self.cache_enabled_checkbox.setChecked(settings['cache_enabled'])
        if 'default_currency' in settings:
            self.default_currency_combo.setCurrentText(settings['default_currency'])
        if 'show_zero_positions' in settings:
            self.show_zero_positions_checkbox.setChecked(settings['show_zero_positions'])
        return True

    def restore_settings(self):
        """Reload the last saved settings into the form on demand."""
        try:
            found = self._apply_saved_settings()
        except Exception as e:
            self._set_status(f"Error restoring settings: {e}", error=True)
            return
        if found:
            self._set_status("Settings restored from last save.")
        else:
            self._set_status("No saved settings found to restore.", error=True)
    
    def save_settings(self):
        """Save current settings."""
        try:
            import json
            import os
            
            # Get the settings file path
            settings_path = "config/settings.json"
            
            # Load existing settings or create default
            settings = {}
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
            
            # Update with current settings
            settings['auto_refresh'] = self.auto_refresh_checkbox.isChecked()
            settings['theme'] = self.theme_combo.currentText()
            settings['refresh_interval'] = self.data_refresh_interval_spin.value()
            settings['data_source'] = self.data_source_combo.currentText()
            settings['cache_enabled'] = self.cache_enabled_checkbox.isChecked()
            settings['default_currency'] = self.default_currency_combo.currentText()
            settings['show_zero_positions'] = self.show_zero_positions_checkbox.isChecked()
            
            # Save settings to file
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            
            self.status_label.setText("Settings saved successfully!")
            self.status_label.setStyleSheet("color: green;")
            
            # Clear status message after 3 seconds
            from PySide6.QtCore import QTimer
            QTimer.singleShot(3000, lambda: self.status_label.setText(""))

        except Exception as e:
            self.status_label.setText(f"Error saving settings: {e}")
            self.status_label.setStyleSheet("color: red;")
    
    def backup_database(self):
        """Back up the live SQLite database to a user-chosen file."""
        import os
        import sqlite3
        from datetime import datetime
        from PySide6.QtWidgets import QFileDialog
        try:
            from database.database import DB_PATH
        except Exception as e:
            self._set_status(f"Cannot locate database: {e}", error=True)
            return

        if not os.path.exists(str(DB_PATH)):
            self._set_status("No database file found to back up.", error=True)
            return

        default_name = f"portfolio_backup_{datetime.now():%Y-%m-%d_%H%M%S}.db"
        dest_path, _ = QFileDialog.getSaveFileName(
            self, "Back Up Database", default_name,
            "SQLite Database (*.db);;All Files (*)"
        )
        if not dest_path:
            return  # user cancelled

        try:
            source = sqlite3.connect(str(DB_PATH))
            try:
                target = sqlite3.connect(dest_path)
                try:
                    source.backup(target)
                finally:
                    target.close()
            finally:
                source.close()
            self._set_status(f"Backup saved to {dest_path}")
        except Exception as e:
            self._set_status(f"Backup failed: {e}", error=True)

    def restore_database(self):
        """Replace the live database with a user-selected backup file."""
        import sqlite3
        from PySide6.QtWidgets import QFileDialog

        try:
            from database.database import DB_PATH, engine
        except Exception as e:
            self._set_status(f"Cannot locate database: {e}", error=True)
            return

        src_path, _ = QFileDialog.getOpenFileName(
            self, "Restore Database", "",
            "SQLite Database (*.db);;All Files (*)"
        )
        if not src_path:
            return  # user cancelled

        # Validate the selected file is genuinely a SQLite database.
        try:
            with open(src_path, "rb") as f:
                header = f.read(16)
        except Exception as e:
            self._set_status(f"Cannot read selected file: {e}", error=True)
            return
        if header != b"SQLite format 3\x00":
            self._set_status(
                "Selected file is not a valid SQLite database.", error=True
            )
            return

        reply = QMessageBox.warning(
            self,
            "Restore Database",
            "This will overwrite your current database with the selected "
            "backup. Any data entered since that backup will be lost.\n\n"
            "Back up first if you are unsure. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            engine.dispose()  # close pooled connections before replacing data
            source = sqlite3.connect(src_path)
            try:
                target = sqlite3.connect(str(DB_PATH))
                try:
                    source.backup(target)
                finally:
                    target.close()
            finally:
                source.close()
        except Exception as e:
            self._set_status(f"Restore failed: {e}", error=True)
            return

        QMessageBox.information(
            self,
            "Restore Complete",
            "Database restored successfully.\n\n"
            "Please restart Portfolio Manager for the changes to take "
            "full effect.",
        )
        self._set_status("Database restored - please restart the application.")

    def _set_status(self, message, error=False):
        """Show a transient message in the settings status label."""
        from PySide6.QtCore import QTimer
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: red;" if error else "color: green;")
        QTimer.singleShot(5000, lambda: self.status_label.setText(""))

    def reset_settings(self):
        """Reset settings to default values."""
        reply = QMessageBox.question(
            self, 
            "Reset Settings", 
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset to default values
            self.auto_refresh_checkbox.setChecked(True)
            self.theme_combo.setCurrentText("Dark")
            self.data_refresh_interval_spin.setValue(5)
            self.data_source_combo.setCurrentText("Yahoo Finance")
            self.cache_enabled_checkbox.setChecked(True)
            self.default_currency_combo.setCurrentText("USD")
            self.show_zero_positions_checkbox.setChecked(False)
            
            self.status_label.setText("Settings reset to defaults!")
            self.status_label.setStyleSheet("color: green;")
            
            # Clear status message after 3 seconds
            from PySide6.QtCore import QTimer
            QTimer.singleShot(3000, lambda: self.status_label.setText(""))