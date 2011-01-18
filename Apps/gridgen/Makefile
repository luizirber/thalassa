check:
	pep8 gridgen
	pylint gridgen

test:
	pep8 tests
	cp -R gridgen/ tests/gridgen
	cp -R examples/data tests/data
	- py.test --testdata=tests/data tests/
	rm -rf tests/gridgen
	rm -rf tests/data
