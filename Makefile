
develop:
	pip install -v -e .[dev] | grep -v link

clean_so:
	find fluidlab -name "*.so" -delete

black:
	black -l 82 fluidlab

tests:
	python -m unittest discover

tests_coverage:
	mkdir -p .coverage
	coverage run -p -m unittest discover

report_coverage:
	coverage combine
	coverage report
	coverage html
	coverage xml
	@echo "Code coverage analysis complete. View detailed report:"
	@echo "file://${PWD}/.coverage/index.html"

coverage: tests_coverage report_coverage
