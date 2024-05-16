import gh
from ansible_vault import Vault  # type: ignore
import yaml

from secrets.schema import Schema, merge_schema, load_secrets, validate_schema
from secrets.config import MainConfig


class Main:
    gh: gh.GithubAction
    vault: Vault
    file_root: str = '.github/secrets-vault'
    main_config: MainConfig
    schemas: dict[str, Schema]
    merged_schemas: dict[str, Schema]

    def __init__(self):
        self.schemas = {}
        self.merged_schemas = {}

    def main(self) -> bool:
        with gh.GithubAction() as gha:
            self.gh = gha
            secret = self.gh.input('VAULT_KEY')
            if not secret:
                raise RuntimeError('VAULT_KEY must be provided')
            self.vault = Vault(secret)
            main_config = self.gh.input('CONFIG', '.github/secrets-vault/config.yml')
            self.file_root = '/'.join(main_config.split('/')[0:-1]) or '.'
            with open(main_config, 'r') as stream:
                config_raw = yaml.safe_load(stream)
                self.main_config = MainConfig.parse_obj(config_raw)
            mode = self.gh.input('MODE', 'export')
            if mode == 'lint':
                return self.do_lint()
            elif mode == 'export':
                return self.do_export()
            else:
                raise ValueError(f'Unsupported mode: {mode}')

    def do_lint(self) -> bool:
        result = True
        for env in self.main_config.environments:
            self.gh.notice(f'Running lint on {env}')
            schema = self.load_schema(env)
            if not validate_schema(schema, self.gh.error):
                result = False
        return result

    def do_export(self) -> bool:
        env = self.gh.input('ENVIRONMENT')
        self.gh.notice(f'Exporting secrets for environment {env}')
        if env not in self.main_config.environments:
            raise KeyError(f'Unsupported environment: {env}')
        schema = self.load_schema(env)
        if not validate_schema(schema, self.gh.error):
            return False
        for key, secret in schema.secrets.items():
            if secret.mask:
                self.gh.add_mask(secret.value)
            if secret.env:
                self.gh.set_env(key, secret.value)
            else:
                self.gh.set_output(key, secret.value)
        return True

    def load_schema(self, environment: str) -> Schema:
        schema = self.parse_schema(environment)
        all_schemas = [schema]
        while schema.parent is not None:
            schema = self.parse_schema(schema.parent)
            all_schemas = [schema] + all_schemas
        merged = all_schemas[0]
        remaining_schemas = all_schemas[1:]
        while len(remaining_schemas) != 0:
            merged = merge_schema(merged, remaining_schemas[0])
            remaining_schemas = remaining_schemas[1:]
        for current_schema in all_schemas:
            self.load_secrets(schema, current_schema)
        return schema

    def parse_schema(self, environment: str) -> Schema:
        filename = f'{self.file_root}/{environment}.yml'
        self.gh.notice('Loading schema', file=filename)
        with open(filename) as f:
            schema_raw = yaml.safe_load(f) or {}
            schema = Schema.parse_obj(schema_raw)
            schema.name = environment
            self.schemas[environment] = schema
            return schema

    def load_secrets(self, schema: Schema, current_schema: Schema | None = None) -> None:
        if current_schema is None:
            current_schema = schema
        vault_file = current_schema.vault_file or f'{self.file_root}/{current_schema.name}.vault'
        self.gh.notice('Loading secrets', file=vault_file)
        with open(vault_file) as f:
            data = self.vault.load(f.read()) or {}
            load_secrets(schema, current_schema, data)


def main():
    import sys
    main = Main()
    if not main.main():
        sys.exit(1)


if __name__ == "__main__":
    main()
