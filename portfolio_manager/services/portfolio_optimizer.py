"""
Portfolio Optimization Service
Implements various portfolio optimization algorithms for the Portfolio Manager.
"""
import sys
import os

# Add the project root to sys.path to ensure imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import List, Dict, Tuple, Optional
from services.portfolio_service import PortfolioService
from database.models import Position

class PortfolioOptimizer:
    """Provides portfolio optimization algorithms for the Portfolio Manager."""
    
    def __init__(self, portfolio_service: PortfolioService):
        """Initialize the portfolio optimizer with a portfolio service instance."""
        self.portfolio_service = portfolio_service
    
    def mean_variance_optimization(self, 
                                 weights: List[float], 
                                 returns: pd.DataFrame,
                                 risk_free_rate: float = 0.02) -> Dict:
        """
        Perform mean-variance optimization using the Markowitz model.
        
        Args:
            weights: Initial weights for optimization
            returns: DataFrame of asset returns
            risk_free_rate: Risk-free rate for Sharpe ratio calculation
            
        Returns:
            Dictionary with optimization results
        """
        try:
            # Calculate expected returns and covariance matrix
            expected_returns = returns.mean()
            cov_matrix = returns.cov()
            
            # Objective function: negative Sharpe ratio (we want to maximize Sharpe)
            def negative_sharpe_ratio(weights, expected_returns, cov_matrix, risk_free_rate):
                portfolio_return = np.sum(weights * expected_returns)
                portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std
                return -sharpe_ratio
            
            # Constraints and bounds
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})
            bounds = tuple((0.0, 1.0) for _ in range(len(weights)))
            
            # Optimize
            result = minimize(negative_sharpe_ratio, 
                            weights, 
                            args=(expected_returns, cov_matrix, risk_free_rate),
                            method='SLSQP',
                            bounds=bounds,
                            constraints=constraints)
            
            if result.success:
                optimized_weights = result.x
                portfolio_return = np.sum(optimized_weights * expected_returns)
                portfolio_std = np.sqrt(np.dot(optimized_weights.T, np.dot(cov_matrix, optimized_weights)))
                sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std
                
                return {
                    'weights': optimized_weights.tolist(),
                    'return': portfolio_return,
                    'risk': portfolio_std,
                    'sharpe_ratio': sharpe_ratio,
                    'success': True
                }
            else:
                return {
                    'weights': weights,
                    'return': 0.0,
                    'risk': 0.0,
                    'sharpe_ratio': 0.0,
                    'success': False,
                    'error': 'Optimization failed'
                }
                
        except Exception as e:
            return {
                'weights': weights,
                'return': 0.0,
                'risk': 0.0,
                'sharpe_ratio': 0.0,
                'success': False,
                'error': str(e)
            }
    
    def risk_parity_optimization(self, returns: pd.DataFrame, 
                               target_risk_contribution: Optional[List[float]] = None) -> Dict:
        """
        Perform risk parity optimization.
        
        Args:
            returns: DataFrame of asset returns
            target_risk_contribution: Target risk contribution percentages (default: equal)
            
        Returns:
            Dictionary with optimization results
        """
        try:
            # Calculate covariance matrix
            cov_matrix = returns.cov()
            
            # If no target risk contributions specified, use equal allocation
            if target_risk_contribution is None:
                n_assets = len(cov_matrix.columns)
                target_risk_contribution = [1.0/n_assets] * n_assets
            
            # Objective function for risk parity
            def risk_parity_objective(weights, cov_matrix, target_risk_contribution):
                # Portfolio risk
                portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
                portfolio_risk = np.sqrt(portfolio_variance)
                
                # Risk contributions
                risk_contributions = []
                for i in range(len(weights)):
                    marginal_contribution = np.dot(weights[i], cov_matrix.iloc[i, :])
                    risk_contribution = np.dot(weights, marginal_contribution) / portfolio_risk
                    risk_contributions.append(risk_contribution)
                
                # Objective: minimize difference from target
                diff = np.array(risk_contributions) - np.array(target_risk_contribution)
                return np.sum(diff**2)
            
            # Initial weights (equal allocation)
            initial_weights = np.array([1.0/len(cov_matrix.columns)] * len(cov_matrix.columns))
            
            # Constraints and bounds
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})
            bounds = tuple((0.0, 1.0) for _ in range(len(cov_matrix.columns)))
            
            # Optimize
            result = minimize(risk_parity_objective,
                            initial_weights,
                            args=(cov_matrix, target_risk_contribution),
                            method='SLSQP',
                            bounds=bounds,
                            constraints=constraints)
            
            if result.success:
                optimized_weights = result.x
                
                # Calculate portfolio metrics
                portfolio_variance = np.dot(optimized_weights.T, np.dot(cov_matrix, optimized_weights))
                portfolio_risk = np.sqrt(portfolio_variance)
                
                # Calculate risk contributions
                risk_contributions = []
                for i in range(len(optimized_weights)):
                    marginal_contribution = np.dot(optimized_weights[i], cov_matrix.iloc[i, :])
                    risk_contribution = np.dot(optimized_weights, marginal_contribution) / portfolio_risk
                    risk_contributions.append(risk_contribution)
                
                return {
                    'weights': optimized_weights.tolist(),
                    'risk': portfolio_risk,
                    'risk_contributions': risk_contributions,
                    'success': True
                }
            else:
                return {
                    'weights': initial_weights.tolist(),
                    'risk': 0.0,
                    'risk_contributions': [0.0] * len(cov_matrix.columns),
                    'success': False,
                    'error': 'Optimization failed'
                }
                
        except Exception as e:
            return {
                'weights': [0.0] * len(returns.columns),
                'risk': 0.0,
                'risk_contributions': [0.0] * len(returns.columns),
                'success': False,
                'error': str(e)
            }
    
    def black_litterman_optimization(self, 
                                   returns: pd.DataFrame,
                                   market_caps: List[float],
                                   views: Dict[str, Dict[str, float]],
                                   risk_aversion: float = 2.5) -> Dict:
        """
        Perform Black-Litterman optimization.
        
        Args:
            returns: DataFrame of asset returns
            market_caps: Market capitalization of assets
            views: Dictionary of views on asset returns
            risk_aversion: Risk aversion parameter
            
        Returns:
            Dictionary with optimization results
        """
        try:
            # Calculate market equilibrium weights
            market_weights = np.array(market_caps) / np.sum(market_caps)
            
            # Calculate expected returns (based on market weights)
            expected_returns = returns.mean()
            
            # Black-Litterman model calculation
            # This is a simplified version - in practice, this would be more complex
            # and would include view matrices and confidence levels
            
            # For simplicity, we'll use a basic approach where we adjust expected returns
            # based on views
            
            # Convert views to array format (simplified)
            adjusted_returns = expected_returns.copy()
            
            # Apply any views (simplified approach)
            for ticker, view in views.items():
                if ticker in adjusted_returns.index:
                    # This is a simplified implementation
                    # In practice, you'd need to properly calculate the Black-Litterman 
                    # posterior expected returns
                    if 'expected_return' in view:
                        adjusted_returns[ticker] = view['expected_return']
            
            # Use mean variance optimization with adjusted returns
            weights = [1.0/len(adjusted_returns)] * len(adjusted_returns)
            
            # Use the mean variance optimization approach with adjusted returns
            optimized_result = self.mean_variance_optimization(
                weights, 
                returns, 
                risk_free_rate=0.02
            )
            
            return optimized_result
            
        except Exception as e:
            return {
                'weights': [0.0] * len(returns.columns),
                'return': 0.0,
                'risk': 0.0,
                'sharpe_ratio': 0.0,
                'success': False,
                'error': str(e)
            }
    
    def efficient_frontier(self, returns: pd.DataFrame, 
                          num_portfolios: int = 100) -> List[Dict]:
        """
        Calculate efficient frontier points.
        
        Args:
            returns: DataFrame of asset returns
            num_portfolios: Number of portfolios to generate
            
        Returns:
            List of portfolio points on efficient frontier
        """
        try:
            # Calculate expected returns and covariance matrix
            expected_returns = returns.mean()
            cov_matrix = returns.cov()
            
            frontier_points = []
            
            # Generate random portfolios and find efficient ones
            for _ in range(num_portfolios):
                # Generate random weights
                weights = np.random.random(len(returns.columns))
                weights = weights / np.sum(weights)  # Normalize
                
                # Calculate portfolio metrics
                portfolio_return = np.sum(weights * expected_returns)
                portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                
                # Store point (return, risk)
                frontier_points.append({
                    'weights': weights.tolist(),
                    'return': portfolio_return,
                    'risk': portfolio_std
                })
            
            # Sort by risk
            frontier_points.sort(key=lambda x: x['risk'])
            
            return frontier_points
            
        except Exception as e:
            return []
    
    def get_portfolio_metrics(self, weights: List[float], returns: pd.DataFrame) -> Dict:
        """
        Calculate portfolio metrics for given weights.
        
        Args:
            weights: Portfolio weights
            returns: DataFrame of asset returns
            
        Returns:
            Dictionary with portfolio metrics
        """
        try:
            # Calculate expected returns and covariance matrix
            expected_returns = returns.mean()
            cov_matrix = returns.cov()
            
            # Calculate portfolio metrics
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # Calculate various risk measures
            portfolio_variance = portfolio_std ** 2
            
            # Calculate Value at Risk (VaR) using historical simulation
            portfolio_returns = np.dot(returns, weights)
            var_95 = np.percentile(portfolio_returns, 5)
            
            # Calculate maximum drawdown (simplified)
            cumulative_returns = (1 + portfolio_returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            return {
                'return': portfolio_return,
                'risk': portfolio_std,
                'var_95': var_95,
                'max_drawdown': max_drawdown,
                'volatility': portfolio_std,
                'expected_return': portfolio_return
            }
            
        except Exception as e:
            return {
                'return': 0.0,
                'risk': 0.0,
                'var_95': 0.0,
                'max_drawdown': 0.0,
                'volatility': 0.0,
                'expected_return': 0.0
            }
