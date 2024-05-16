from typing import Optional
from io import FileIO
import os


class GithubAction:
    github_env: Optional[FileIO] = None
    github_step_summary: Optional[FileIO] = None
    github_output: Optional[FileIO] = None

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
        if self.github_output is not None:
            self.github_output.close()

    def env_file(self):
        if self.github_env is None:
            self.github_env = open(os.environ.get('GITHUB_ENV'), 'a')
        return self.github_env

    def output_file(self):
        if self.github_output is None:
            self.github_output = open(os.environ.get('GITHUB_OUTPUT'), 'a')
        return self.github_output

    def workflow_command(self, cmd: str, val: str, **kwargs):
        line = f'::{cmd}'
        cont = ' '
        if kwargs:
            for k, v in kwargs.items():
                if v is None:
                    continue
                line += f'{cont}{k}={v}'
                cont = ','
        line += f'::{val}'
        print(line, flush=True)

    def set_output(self, var, val):
        print(f'{var}={val}', file=self.output_file(), flush=True)

    def add_mask(self, val):
        self.workflow_command('add-mask', val)

    def set_secret(self, var, val):
        self.add_mask(val)
        self.set_output(var, val)

    def error(self, msg):
        self.workflow_command('error', msg)

    def notice(self, msg, file=None):
        self.workflow_command('notice', msg, file=file)

    def set_env(self, var, val):
        print(f'{var}={val}', file=self.env_file(), flush=True)

    def input(self, var, default=None):
        r = os.environ.get(f'INPUT_{var}', default)
        if default is None and not r:
            raise KeyError(f'INPUT {var} not set')
        return r
