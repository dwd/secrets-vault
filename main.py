import gh
from ansible_vault import Vault
from pydantic import BaseModel
import yaml


class MainConfig(BaseModel):
    environments: list[str] = ['main']


class Secret(BaseModel):
    description: str
    mask: bool = True
    env: bool = False
    output_file: str | None = None
    input_file: str | None = None
    optional: bool = False
    final: bool = False
    value: str | None = None


class Schema(BaseModel):
    name: str | None = None
    parent: str | None = None
    abstract: bool = False
    vault_file: str | None = None
    secrets: dict[str, Secret] = {}


class Main:
    gh: gh.GithubAction
    vault: Vault
    file_root: str = '.github/secrets-vault'
    main_config: MainConfig
    schemas: dict[str, Schema]

    def __init__(self):
        self.schemas = {}

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
                self.do_lint()
            elif mode == 'export':
                self.do_export()

    def do_export(self) -> None:
        env = self.gh.input('ENVIRONMENT')
        self.gh.info(f'Exporting secrets for environment {env}')
        schema = self.parse_schema(env)
        self.load_secrets(schema)
        for key, secret in schema.secrets.items():
            if secret.mask:
                self.gh.add_mask(secret.value)
            if secret.env:
                self.gh.set_env(key, secret.value)
            else:
                self.gh.set_output(key, secret.value)

    def load_schema(self, environment: str) -> Schema:
        schema = self.parse_schema(environment)
        self.load_secrets(schema)
        return schema

    def parse_schema(self, environment: str) -> Schema:
        filename = f'{self.file_root}/{environment}.yml'
        self.gh.info(f'Loading schema from {filename}')
        with open(filename) as f:
            schema_raw = yaml.safe_load(f) or {}
            schema = Schema.parse_obj(schema_raw)
            schema.name = environment
            self.schemas[environment] = schema
            return schema

    def load_secrets(self, schema: Schema):
        vault_file = schema.vault_file or f'{self.file_root}/{schema.name}.vault'
        self.gh.info(f'Loading secrets from {vault_file}')
        with open(vault_file) as f:
            data = self.vault.load(f.read())
            for key in set(schema.secrets.keys()).union(set(data.keys())):
                if key not in schema.secrets:
                    raise KeyError(f'Key {key} not found in schema {schema.name}')
                if key in data:
                    schema.secrets[key].value = data[key]
                elif not schema.optional:
                    raise ValueError(f'Key {key} not found in vault {schema.name}')


def main():
    import sys
    main = Main()
    if not main.main():
        sys.exit(1)


if __name__ == "__main__":
    main()
