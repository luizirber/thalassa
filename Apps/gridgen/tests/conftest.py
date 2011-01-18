# py.test configuration


def pytest_addoption(parser):
    parser.addoption('--testdata', action="store",
        help="data directory for tests")


def pytest_funcarg__testdata(request):
    return request.config.option.testdata
