echo "== TESTS =="
coverage run --source mud test/test.py
echo "== COVERAGE =="
coverage report -m