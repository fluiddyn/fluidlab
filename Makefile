
clean_so:
	find fluidlab -name "*.so" -delete

tests:
	python -m unittest discover

develop:
	python setup.py develop
