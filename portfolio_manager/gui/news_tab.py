"""
News System for Portfolio Manager with RSS Feeds
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLabel, QComboBox, QPushButton, QTableWidget,
                              QTableWidgetItem, QGroupBox, QSplitter, QTextEdit,
                              QFileDialog, QMessageBox, QCheckBox, QProgressBar,
                              QStatusBar)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon
import feedparser
import requests
from datetime import datetime
import time
from typing import List, Dict
import threading


class RSSFeedWorker(QThread):
    """Worker thread for fetching RSS feeds."""
    
    # Signals for communication with main thread
    feed_fetched = Signal(list)
    error_occurred = Signal(str)
    progress_updated = Signal(int, int)
    
    def __init__(self, feed_urls: List[str]):
        super().__init__()
        self.feed_urls = feed_urls
        self.running = True
        
    def run(self):
        """Fetch RSS feeds in background thread."""
        try:
            all_entries = []
            total_feeds = len(self.feed_urls)
            
            for i, feed_url in enumerate(self.feed_urls):
                if not self.running:
                    break
                    
                try:
                    # Parse the RSS feed
                    feed = feedparser.parse(feed_url)
                    
                    # Process entries
                    for entry in feed.entries[:10]:  # Limit to 10 entries per feed
                        if not self.running:
                            break
                            
                        entry_data = {
                            'title': entry.get('title', 'No title'),
                            'summary': entry.get('summary', 'No summary'),
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'feed': feed.get('feed', {}).get('title', 'Unknown Feed'),
                            'source': feed_url
                        }
                        all_entries.append(entry_data)
                        
                        # Update progress
                        self.progress_updated.emit(i + 1, total_feeds)
                        
                except Exception as e:
                    print(f"Error fetching {feed_url}: {e}")
                    self.error_occurred.emit(f"Error fetching {feed_url}: {str(e)}")
                    continue
                    
            # Sort by publication date (newest first)
            if all_entries:
                all_entries.sort(key=lambda x: x.get('published', ''), reverse=True)
            
            self.feed_fetched.emit(all_entries)
            
        except Exception as e:
            print(f"Error in RSS worker: {e}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(f"Error in RSS worker: {str(e)}")


class NewsFeedManager:
    """Manages RSS feeds for the news system."""
    
    def __init__(self):
        # Predefined financial RSS feeds
        self.default_feeds = [
            "https://feeds.bbci.co.uk/news/business/rss.xml",
            "https://feeds.reuters.com/reuters/businessNews",
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            "https://www.marketwatch.com/tools/rss/rss.aspx",
            "https://www.investing.com/news/rss",
            "https://www.theguardian.com/uk-news/rss",
            "https://www.bloomberg.com/feed/podcast/bloomberg-tech.xml"
        ]
        
        # Additional custom feeds can be added here
        self.custom_feeds = []
        
    def get_all_feeds(self) -> List[str]:
        """Get all active RSS feeds."""
        return self.default_feeds + self.custom_feeds


class NewsTab(QWidget):
    """News system tab with RSS feed support."""
    
    def __init__(self):
        """Initialize news tab."""
        super().__init__()
        self.news_manager = NewsFeedManager()
        self.current_entries = []
        self.worker = None
        self.timer = None
        self.init_ui()
        self.load_default_feeds()
        self.setup_feeds_timer()
        
    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        
        # Create a splitter for main content
        splitter = QSplitter(Qt.Vertical)
        
        # Feed configuration and controls
        controls_group = QGroupBox("Feed Configuration")
        controls_layout = QFormLayout(controls_group)
        
        self.feed_combo = QComboBox()
        self.feed_combo.addItems(["BBC Business", "Reuters", "CNBC", "MarketWatch", "Investing.com", "The Guardian", "Bloomberg"])
        
        self.refresh_btn = QPushButton("Refresh News")
        self.refresh_btn.clicked.connect(self.refresh_news)
        
        self.auto_refresh_checkbox = QCheckBox("Auto-refresh every 15 minutes")
        self.auto_refresh_checkbox.setChecked(True)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        controls_layout.addRow("Feed Source:", self.feed_combo)
        controls_layout.addRow("", self.refresh_btn)
        controls_layout.addRow("", self.auto_refresh_checkbox)
        controls_layout.addRow("", self.progress_bar)
        
        # News table
        self.news_table = QTableWidget(0, 4)
        self.news_table.setHorizontalHeaderLabels(["Title", "Feed", "Date", "Summary"])
        self.news_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.news_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.news_table.itemClicked.connect(self.on_news_selected)
        
        # News detail view
        self.news_detail = QTextEdit()
        self.news_detail.setReadOnly(True)
        self.news_detail.setMaximumHeight(150)
        
        # Add components to splitter
        splitter.addWidget(controls_group)
        splitter.addWidget(self.news_table)
        splitter.addWidget(self.news_detail)
        
        layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
        
        # Set splitter sizes
        splitter.setSizes([100, 300, 150])
        
    def load_default_feeds(self):
        """Load default feeds."""
        self.status_bar.showMessage("Ready to fetch news feeds")
        
    def setup_feeds_timer(self):
        """Set up auto-refresh timer."""
        try:
            self.timer = QTimer()
            self.timer.timeout.connect(self.refresh_news)
            if self.auto_refresh_checkbox.isChecked():
                self.timer.start(15 * 60 * 1000)  # 15 minutes in milliseconds
        except Exception as e:
            print(f"Error setting up timer: {e}")
            
    def refresh_news(self):
        """Fetch news from RSS feeds."""
        try:
            if self.worker and self.worker.isRunning():
                self.status_bar.showMessage("News refresh already in progress...")
                return
                
            self.status_bar.showMessage("Fetching news feeds...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Create and start worker thread
            self.worker = RSSFeedWorker(self.news_manager.get_all_feeds())
            self.worker.feed_fetched.connect(self.on_feeds_fetched)
            self.worker.error_occurred.connect(self.on_error)
            self.worker.progress_updated.connect(self.on_progress_update)
            
            self.worker.start()
            
        except Exception as e:
            self.status_bar.showMessage(f"Error starting news refresh: {str(e)}")
            print(f"Error in refresh_news: {e}")
            import traceback
            traceback.print_exc()
            
    def on_feeds_fetched(self, entries: List[Dict]):
        """Handle fetched feeds."""
        try:
            self.current_entries = entries
            self.display_news()
            self.status_bar.showMessage(f"Fetched {len(entries)} news items")
            self.progress_bar.setVisible(False)
        except Exception as e:
            print(f"Error in on_feeds_fetched: {e}")
            self.status_bar.showMessage(f"Error displaying news: {str(e)}")
            self.progress_bar.setVisible(False)
            
    def on_progress_update(self, current: int, total: int):
        """Handle progress updates from worker."""
        try:
            self.progress_bar.setValue(int((current / total) * 100))
        except Exception as e:
            print(f"Error in on_progress_update: {e}")
            
    def display_news(self):
        """Display news in table."""
        self.news_table.setRowCount(len(self.current_entries))
        
        for i, entry in enumerate(self.current_entries):
            title_item = QTableWidgetItem(entry['title'][:100] + "..." if len(entry['title']) > 100 else entry['title'])
            feed_item = QTableWidgetItem(entry['feed'])
            date_item = QTableWidgetItem(entry['published'][:20] if entry['published'] else 'Unknown')
            summary_item = QTableWidgetItem(entry['summary'][:100] + "..." if len(entry['summary']) > 100 else entry['summary'])
            
            self.news_table.setItem(i, 0, title_item)
            self.news_table.setItem(i, 1, feed_item)
            self.news_table.setItem(i, 2, date_item)
            self.news_table.setItem(i, 3, summary_item)
            
    def on_news_selected(self, item):
        """Handle news selection."""
        row = item.row()
        if 0 <= row < len(self.current_entries):
            entry = self.current_entries[row]
            self.news_detail.setPlainText(f"{entry['title']}\n\n{entry['summary']}")
            
    def on_error(self, error_msg: str):
        """Handle errors."""
        print(f"News Error: {error_msg}")
        self.status_bar.showMessage(f"Error: {error_msg}")
        self.progress_bar.setVisible(False)