"""
Portfolio analytics and reporting module for Portfolio Manager
"""

import pandas as pd
import numpy as np
from datetime import datetime
from services.portfolio_service import PortfolioService

class PortfolioAnalytics:
    """Provides analytics and reporting for portfolio data."""
    
    def __init__(self, portfolio_service):
        """Initialize analytics with portfolio service."""
        self.portfolio_service = portfolio_service
    
    def get_portfolio_summary(self):
        """Get summary statistics for the portfolio."""
        positions = self.portfolio_service.get_positions()
        
        if not positions:
            return {
                'total_positions': 0,
                'total_cost': 0.0,
                'total_value': 0.0,
                'total_gain_loss': 0.0,
                'total_gain_loss_percent': 0.0
            }
        
        total_cost = 0.0
        total_value = 0.0
        
        for position in positions:
            cost = position.purchase_price * position.shares
            current_price = self.portfolio_service.get_current_price(position.ticker)
            if current_price:
                value = current_price * position.shares
            else:
                value = cost  # If no current price, use cost basis
                
            total_cost += cost
            total_value += value
        
        total_gain_loss = total_value - total_cost
        total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
        
        return {
            'total_positions': len(positions),
            'total_cost': total_cost,
            'total_value': total_value,
            'total_gain_loss': total_gain_loss,
            'total_gain_loss_percent': total_gain_loss_percent
        }
    
    def get_position_performance(self):
        """Get performance data for individual positions."""
        positions = self.portfolio_service.get_positions()
        
        # Get all current prices at once
        prices = self.portfolio_service.get_current_prices(positions)
        
        performance_data = []
        for position in positions:
            cost = position.purchase_price * position.shares
            current_price = prices.get(position.ticker, {}).get('current_price', 0)
            
            if current_price:
                value = current_price * position.shares
                gain_loss = value - cost
                gain_loss_percent = (gain_loss / cost * 100) if cost > 0 else 0
            else:
                value = cost
                gain_loss = 0
                gain_loss_percent = 0
            
            performance_data.append({
                'ticker': position.ticker,
                'company_name': position.company_name,
                'shares': position.shares,
                'purchase_price': position.purchase_price,
                'current_price': current_price or 0,
                'cost_basis': cost,
                'market_value': value,
                'gain_loss': gain_loss,
                'gain_loss_percent': gain_loss_percent
            })
        
        return performance_data
    
    def get_portfolio_distribution(self):
        """Get portfolio distribution by sector (if available)."""
        # For now, return basic distribution by ticker
        positions = self.portfolio_service.get_positions()
        
        # Get all current prices at once
        prices = self.portfolio_service.get_current_prices(positions)
        
        distribution = {}
        total_value = 0
        
        for position in positions:
            current_price = prices.get(position.ticker, {}).get('current_price', 0)
            if current_price:
                value = current_price * position.shares
                distribution[position.ticker] = value
                total_value += value
        
        # Convert to percentages
        if total_value > 0:
            for ticker in distribution:
                distribution[ticker] = (distribution[ticker] / total_value) * 100
        
        return distribution
    
    def generate_report(self):
        """Generate a complete portfolio report."""
        summary = self.get_portfolio_summary()
        performance = self.get_position_performance()
        distribution = self.get_portfolio_distribution()
        
        report = {
            'summary': summary,
            'performance': performance,
            'distribution': distribution,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return report

# Create a simple function to format currency
def format_currency(amount):
    """Format currency for display."""
    return f"${amount:,.2f}"

# Create a simple function to format percentages
def format_percentage(percent):
    """Format percentage for display."""
    return f"{percent:+.2f}%"