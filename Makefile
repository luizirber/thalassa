pep8:
	pep8 --exclude="thalassa_rc.py,qtui.py" thalassa

pylint:
	pylint -d c --ignore=thalassa_rc.py --ignore=qtui.py thalassa

pyflakes:
	pyflakes thalassa

clonedigger: clean
	clonedigger -o tests/output.html thalassa

check: pep8 pylint pyflakes clonedigger

clean:
	- rm thalassa/ui/qtmplui/qtui.py thalassa/ui/qtmplui/thalassa_rc.py
	- rm -rf dist build MANIFEST
	- find . -iname '*.pyc' -exec rm {} +

build: clean
	python setup.py build

sdist: clean
	python setup.py sdist

wininst: clean
	python setup.py bdist --format=wininst
