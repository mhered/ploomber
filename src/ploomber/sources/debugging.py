from pathlib import Path
import tempfile
import inspect

import jupyter_client
import papermill
import parso
import nbformat


class CallableDebugger:
    """

    Examples
    --------
    >>> CallableDebugger(fn, {'param': 1})
    >>> tmp = debugger._to_nb()
    >>> tmp # modify tmp notebook
    >>> debugger._overwrite_from_nb(tmp)
    """

    def __init__(self, fn, params):
        self.fn = fn
        self.file = inspect.getsourcefile(fn)
        # how do we deal with def taking more than one line?
        lines, start = inspect.getsourcelines(fn)
        self.lines = (start, start + len(lines))
        self.params = params
        _, self.tmp_path = tempfile.mkstemp(suffix='.ipynb')

    def _to_nb(self):
        """
        Returns the function's body in a notebook (tmp location), insert
        injected parameters
        """
        callable_to_nb(self.fn, self.tmp_path)

        papermill.execute_notebook(self.tmp_path, self.tmp_path,
                                   prepare_only=True,
                                   parameters=self.params)

        return self.tmp_path

    def _overwrite_from_nb(self, path):
        """
        Overwrite the function's body with the notebook contents, excluding
        injected parameters and cells whose first line is #
        """
        # add leading space
        nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)

        code_cells = [c['source'] for c in nb.cells if c['cell_type'] == 'code'
                      and 'injected-parameters' not in c['metadata']['tags']
                      and c['source'][:2] != '#\n']

        # add 4 spaces to each code cell, exclude white space lines
        code_cells = [indent_cell(code) for code in code_cells]

        content = Path(self.file).read_text().splitlines()

        new_content = (content[:self.lines[0]]
                       + code_cells + content[self.lines[1]:])

        Path(self.file).write_text('\n'.join(new_content))

    def __enter__(self):
        self.tmp_path = self._to_nb()
        return self.tmp_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._overwrite_from_nb(self.tmp_path)
        Path(self.tmp_path).unlink()

    def __del__(self):
        tmp = Path(self.tmp_path)
        if tmp.exists():
            tmp.unlink()


def indent_line(l):
    return '    ' + l if l else ''


def indent_cell(code):
    return '\n'.join([indent_line(l) for l in code.splitlines()])


def callable_to_nb(fn, path):
    """
    Converts a Python function to a notebook
    """
    # TODO: exclude return at the end, what if we find more than one?
    # maybe do not support functions with return statements for now
    s = inspect.getsource(fn)
    module = parso.parse(s)
    statements = module.children[0].children[-1]

    nb_format = nbformat.versions[nbformat.current_nbformat]
    nb = nb_format.new_notebook()

    for statement in statements.children:
        lines = [l[4:] for l in statement.get_code().split('\n')]
        cell = nb_format.new_code_cell(source='\n'.join(lines))
        nb.cells.append(cell)

    k = jupyter_client.kernelspec.get_kernel_spec('python3')

    nb.metadata.kernelspec = {
            "display_name": k.display_name,
            "language": k.language,
            "name": 'python3'
        }

    nbformat.write(nb, path)


def nb_to_callable_source(path):
    pass