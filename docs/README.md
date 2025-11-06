# Documentation

This directory contains the Sphinx documentation for the Weather Activity Recommendation API.

## Features

- **Automatic API Discovery**: Uses sphinx-autoapi to automatically discover and document all modules in `app/` and `tests/`
- **Dynamic Documentation**: No need to manually update .rst files when adding new modules or functions
- **Modern Theme**: Uses Read the Docs theme for professional appearance
- **Multiple Formats**: Supports reStructuredText and Markdown
- **Interactive Features**: Includes source code viewing and cross-references

## Building Documentation

### Prerequisites

Install the documentation dependencies:

```bash
pip install -r ../requirements.txt
```

### Build Methods

**Method 1: Using Sphinx directly**
```bash
cd docs
sphinx-build -b html source _build/html
```

**Method 2: Using the build script**
```bash
cd docs
python build_docs.py
```

**Method 3: Using make (Unix/Linux/Mac)**
```bash
cd docs
make html
```

**Method 4: Using make.bat (Windows)**
```bash
cd docs
make.bat html
```

### Live Reload (Development)

For continuous documentation development:

```bash
pip install sphinx-autobuild
cd docs
sphinx-autobuild source _build/html
```

This will start a local server and automatically rebuild when files change.

## Structure

```
docs/
├── source/
│   ├── conf.py           # Sphinx configuration
│   ├── index.rst         # Main documentation page
│   ├── overview.rst      # Project overview
│   ├── api_reference.rst # API documentation
│   ├── _static/          # Custom CSS and assets
│   └── _templates/       # Custom templates
├── _build/               # Generated documentation
├── Makefile             # Unix/Linux build commands
├── make.bat             # Windows build commands
└── build_docs.py        # Python build script
```

## Configuration

The main configuration is in `source/conf.py`. Key settings:

- **autoapi_dirs**: Directories to automatically document (`['../../app', '../../tests']`)
- **autoapi_options**: What to include in documentation (members, inheritance, etc.)
- **html_theme**: Uses `sphinx_rtd_theme` for professional appearance
- **extensions**: Includes napoleon for Google/NumPy docstrings, autoapi for discovery

## Automatic Documentation

The setup automatically documents:

- **app/main.py**: FastAPI application entry point
- **app/data/**: Data storage and management modules
- **app/models/**: All data models (db, requests, response)
- **app/routes/**: All API route definitions
- **app/services/**: Business logic and external service integrations
- **tests/**: All test modules and functions

## Adding Documentation

### For New Modules

No action needed! AutoAPI will automatically discover and document any new Python files added to the `app/` or `tests/` directories.

### For Better Documentation

Add docstrings to your Python code:

```python
def example_function(param1: str, param2: int) -> bool:
    """Example function with Google-style docstring.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: If param2 is negative
    """
    if param2 < 0:
        raise ValueError("param2 must be non-negative")
    return True
```

### For Additional Pages

Add new .rst or .md files to `source/` and include them in the toctree in `index.rst`.

## Viewing Documentation

After building, open `_build/html/index.html` in your browser.

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
2. **Missing Modules**: Check that the paths in `autoapi_dirs` are correct
3. **Build Failures**: Check the error messages and ensure all Python files have valid syntax

### Cleaning Builds

To clean the build directory:

```bash
cd docs
rm -rf _build  # Unix/Linux/Mac
rmdir /s _build  # Windows
```

Or use the clean target:

```bash
make clean      # Unix/Linux/Mac
make.bat clean  # Windows
```