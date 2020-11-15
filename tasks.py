"""
Setup tasks (requires invoke: pip install invoke)
"""
from pathlib import Path
import base64
from invoke import task


@task
def db_credentials(c):
    """
    """
    path = str(Path('~', '.auth', 'postgres-ploomber.json').expanduser())
    creds = Path(path).read_text()
    print(base64.b64encode(creds.encode()).decode())


@task
def setup(c):
    c.run('conda create --name ploomber python=3.8 --yes')
    c.run('eval "$(conda shell.bash hook)" '
          '&& conda install graphviz r-base r-irkernel --yes'
          '&& conda activate ploomber '
          '&& pip install --editable .[all]')
    print('Done! Activate your environment with:\nconda activate ploomber')
