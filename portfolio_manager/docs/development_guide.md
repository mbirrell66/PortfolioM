# Portfolio Manager Development Guide

## Project Structure

```
portfolio_manager/
├── main.py                    # Application entry point
├── config/
│   └── settings.json         # Application configuration
├── data/
│   └── portfolio.db          # SQLite database file
├── database/
│   ├── models.py             # Database models
│   └── database.py           # Database connection and initialization
├── gui/
│   ├── main_window.py        # Main application window
│   ├── add_position_dialog.py # Dialog for adding positions
│   ├── edit_position_dialog.py # Dialog for editing positions
│   └── dashboard_widget.py   # Portfolio analytics dashboard
├── services/
│   ├── portfolio_service.py   # Portfolio management operations
│   ├── market_data_service.py # Market data integration
│   └── portfolio_analytics.py # Portfolio analytics and reporting
├── tests/
│   ├── test_database.py      # Database tests
│   ├── test_analytics.py     # Analytics tests
│   └── test_integration.py   # Integration tests
├── docs/
│   ├── user_guide.md         # User documentation
│   └── api_docs.md           # API documentation
├── requirements.txt          # Dependencies
├── setup.py                  # Package configuration
└── .gitignore                # Version control exclusions
```

## Development Setup

### Prerequisites
- Python 3.13
- Git
- Virtual environment (recommended)

### Installation Steps

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests to verify installation:**
   ```bash
   pytest tests/
   ```

## Coding Standards

### Python Style Guide
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all public methods
- Keep functions focused and small
- Use meaningful variable and function names

### Database Guidelines
- Use SQLAlchemy ORM for database operations
- Handle database sessions properly with context managers
- Validate data before database operations
- Use transactions for multiple related operations

### GUI Guidelines
- Use PySide6 consistently
- Follow Qt design patterns
- Implement proper error handling
- Use meaningful naming conventions

## Testing Strategy

### Unit Tests
Located in `tests/` directory:
- `test_database.py`: Tests database models and operations
- `test_analytics.py`: Tests analytics and formatting functions
- `test_integration.py`: Tests integration between components

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=services --cov=database

# Run specific test file
pytest tests/test_database.py

# Run with verbose output
pytest tests/ -v
```

## Adding New Features

1. **Create new module**: Add to appropriate directory (services, gui, etc.)
2. **Add tests**: Create corresponding test files
3. **Update documentation**: Add to docs/
4. **Follow existing patterns**: Use same structure and conventions
5. **Run all tests**: Ensure no regressions

## Deployment

### For End Users
1. Install dependencies: `pip install -r requirements.txt`
2. Run application: `python main.py`

### For Developers
1. Ensure all tests pass
2. Update documentation
3. Create release package: `python setup.py sdist`
4. Publish to PyPI (if configured)

## Version Control

### Branching Strategy
- `main`: Stable production code
- `develop`: Active development
- Feature branches: For new features

### Commit Guidelines
- Use descriptive commit messages
- Follow conventional commit format
- Keep commits focused and atomic
- Include relevant issue numbers

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Write tests
5. Update documentation
6. Submit pull request

## License

MIT License - see LICENSE file for details.