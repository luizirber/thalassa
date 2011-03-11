pep8:
	pep8 --exclude="gridgen_rc.py,qtui.py" gridgen

pylint:
	pylint -d c --ignore=gridgen_rc.py --ignore=qtui.py gridgen

pyflakes:
	pyflakes gridgen

clonedigger: clean
	clonedigger -o tests/output.html gridgen

check: pep8 pylint pyflakes clonedigger

clean:
	- rm gridgen/ui/qtmplui/qtui.py gridgen/ui/qtmplui/gridgen_rc.py
	- rm -rf dist build MANIFEST

build: clean
	python setup.py build

sdist: clean
	python setup.py sdist
