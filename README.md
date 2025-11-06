python3.12 -m pytest

python3.12 -m uvicorn app.main:app --reload



dynamic test:
python -m pytest tests/test_dynamic.py -vv


run sphinx:

sphinx-build -b html source _build/html
python -m http.server 8080
