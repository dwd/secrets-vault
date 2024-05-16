from typing import Optional
from io import FileIO
import os


class GithubAction:
    github_env: Optional[FileIO] = None
    github_step_summary: Optional[FileIO] = None

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error(str(exc_val))
        if self.github_step_summary is not None:
            self.github_step_summary.close()
        if self.github_env is not None:
            self.github_env.close()

    def env_file(self):
        if self.github_env is None:
            self.github_env = open(os.environ.get('GITHUB_ENV'), 'a')
        return self.github_env

    def workflow_command(self, cmd: str, val: str, **kwargs):
        line = f'::{cmd}'
        cont = ' '
        if kwargs:
            for k, v in kwargs.items():
                line += f'{cont}{k}={v}'
                cont = ','
        line += f'::{val}'
        print(line, flush=True)

    def set_output(self, var, val):
        self.workflow_command('set-output', val, name=var)

    def add_mask(self, val):
        self.workflow_command('add-mask', val)

    def set_secret(self, var, val):
        self.add_mask(val)
        self.set_output(var, val)

    def error(self, msg):
        self.workflow_command('error', msg)

    def info(self, msg):
        self.workflow_command('info', msg)

    def set_env(self, var, val):
        print(f'{var}={val}', file=self.env_file(), flush=True)

    def input(self, var, default=None):
        r = os.environ.get(f'INPUT_{var}', default)
        if default is None and not r:
            for k in os.environ.keys():
                if k.startswith('INPUT_'):
                    self.info(f'Found possible input {k}')
                else:
                    self.info(f'Other envvar {k}')
            raise KeyError(f'INPUT {var} not set')
        return r
