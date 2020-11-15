from pathlib import Path
import os
import copy
import sys

import pytest
from ploomber.util.util import add_to_sys_path, load_dotted_path, chdir_code


def test_add_to_sys_path():
    path = str(Path('/path/to/add').resolve())

    with add_to_sys_path(path, chdir=False):
        assert path in sys.path

    assert path not in sys.path


def test_add_to_sys_path_with_chdir(tmp_directory):
    path = Path('.').resolve() / 'some_directory'
    path.mkdir()
    path = str(path)
    old_dir = os.getcwd()

    with add_to_sys_path(path, chdir=True):
        assert path in sys.path
        assert path == os.getcwd()

    assert path not in sys.path
    assert old_dir == os.getcwd()


def test_add_to_sys_path_with_none():
    original = copy.copy(sys.path)

    with add_to_sys_path(None, chdir=False):
        assert sys.path == original

    assert sys.path == original


def test_add_to_sys_path_with_exception():
    path = str(Path('/path/to/add').resolve())

    with pytest.raises(Exception):
        with add_to_sys_path(path, chdir=False):
            assert path in sys.path
            raise Exception

    assert path not in sys.path


def test_load_dotted_path_custom_error_message():
    with pytest.raises(AttributeError) as excinfo:
        load_dotted_path('test_pkg.not_a_function')

    assert ('Could not get "not_a_function" from module "test_pkg"'
            in str(excinfo.value))


def test_chdir_code(tmp_directory):
    # test generated code is valid
    eval(chdir_code(tmp_directory))
