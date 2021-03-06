import os
import ast
import pytest


_SKIP_FILES = ['setup.py', '__init__.py', 'setup_package.py']


def pytest_addoption(parser):
    group = parser.getgroup('docstring')
    group.addoption(
        '--docstring',
        action='store_true',
        dest='docstring',
        help='validate docstrings for public functions'
    )
    group.addoption(
        '--test-private',
        action='store_true',
        dest='test_private',
        help='test docstrings for private functions as well'
    )

def pytest_collect_file(parent, path):
    # Look only at Python source files
    if not path.ext == '.py':
        return None

    # Ignore other tests
    if path.basename.startswith('test_'):
        return None

    if path.basename in _SKIP_FILES:
        return None

    return DocstringFile(path, parent)

def _temp_module_name(path):
    pathlist = os.path.splitext(path)[0].split(os.path.sep)
    return "_doctstring.{}".format('.'.join(pathlist))

class DocstringFile(pytest.File):
    def collect(self):
        source = self.fspath.open()
        module = ast.parse(source.read())
        for node in module.body:
            # TODO: eventually this should be configurable from the command line
            if hasattr(node, 'name') and node.name.startswith('_'):
                continue
            if isinstance(node, ast.FunctionDef):
                yield DocstringFuncItem('function:' + node.name, self, node)
            elif isinstance(node, ast.ClassDef):
                yield DocstringClassItem('class:' + node.name, self, node)
                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        name = node.name + '.' + method.name
                        yield DocstringFuncItem(
                            'method:' + name, self, node, method=True)

def _check_missing_docstring(node, label):
    docstring = ast.get_docstring(node)
    if docstring is None:
        raise DocstringMissingException(
            "Public {} '{}' is missing a docstring".format(label, node.name))

class DocstringFuncItem(pytest.Item):
    def __init__(self, name, parent, node, method=False):
        super(DocstringFuncItem, self).__init__(name, parent)
        self.node = node
        self.method = method

    def runtest(self):
        label = 'method' if self.method else 'function'
        _check_missing_docstring(self.node, label)

    def reportinfo(self):
        return self.fspath, self.node.lineno, "[docstring] %s" % self.name

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, DocstringMissingException):
            return str(excinfo.value)

class DocstringClassItem(pytest.Item):
    def __init__(self, name, parent, cls):
        super(DocstringClassItem, self).__init__(name, parent)
        self.cls = cls

    def reportinfo(self):
        return self.fspath, self.cls.lineno, "[docstring] %s" % self.name

    def runtest(self):
        _check_missing_docstring(self.cls, 'class')

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, DocstringMissingException):
            return str(excinfo.value)

class DocstringMissingException(Exception):
    """ Custom exception to indicate missing docstring for public function """
