"""
Database module initialization
"""
from .models import Base as PortfolioBase
from .personal_finance_models import Base as PersonalFinanceBase
from .tax_models import Base as TaxBase

# Combine all bases for database initialization
AllBases = [PortfolioBase, PersonalFinanceBase, TaxBase]