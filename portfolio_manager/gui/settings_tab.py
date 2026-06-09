"""
Settings tab for Portfolio Manager
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLabel, QComboBox, QPushButton, QCheckBox,
                              QSpinBox, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt


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
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(save_btn)
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
        """Load saved settings from file."""
        try:
            import json
            import os
            
            # Get the settings file path
            settings_path = "config/settings.json"
            
            # Check if settings file exists
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                
                # Load settings values
                if 'auto_refresh' in settings:
                    self.auto_refresh_checkbox.setChecked(settings['auto_refresh'])
                if 'refresh_interval' in settings:
                    self.data_refresh_interval_spin.setValue(settings['refresh_interval'])
                if 'default_currency' in settings:
                    self.default_currency_combo.setCurrentText(settings['default_currency'])
        except Exception as e:
            print(f"Error loading settings: {e}")
    
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
            settings['refresh_interval'] = self.data_refresh_interval_spin.value()
            settings['default_currency'] = self.default_currency_combo.currentText()
            
            # Save settings to file
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            
            self.status_label.setText("Settings saved successfully!")
            self.status_label.setStyleSheet("color: green;")
            
            # Clear status message after 3 seconds
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(3000, lambda: self.status_label.setText(""))
            
        except Exception as e:
            self.status_label.setText(f"Error saving settings: {e}")
            self.status_label.setStyleSheet("color: red;")
    
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
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(3000, lambda: self.status_label.setText(""))