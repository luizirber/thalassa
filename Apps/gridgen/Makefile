pep8:
	pep8 --exclude="gridgen_rc.py,qtui.py" gridgen

pylint:
	pylint -d c --ignore=gridgen_rc.py --ignore=qtui.py gridgen

pyflakes:
	pyflakes gridgen

clonedigger:
	- rm gridgen/ui/qtmplui/qtui.py gridgen/ui/qtmplui/gridgen_rc.py
	clonedigger -o tests/output.html gridgen

check: pep8 pylint pyflakes clonedigger
