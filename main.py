import gh
from ansible.parsing.vault import VaultLib
from pydantic import BaseModel
import yaml


class MainConfig(BaseModel):
    environments: list[str] = ['main']


class Secret(BaseModel):
    mask: bool = True
    env: bool = False
    output_file: str | None = None
    input_file: str | None = None
    optional: bool = False
    final: bool = False
    value: str | None = None


class Schema(BaseModel):
    name: str | None
    parent: str | None = None
    abstract: bool = False
    vault_file: str | None = None
    secrets: dict[str, Secret]


class Main:
    gh: gh.GithubAction
    vault_lib = VaultLib
    file_root: str = '.github/secrets-vault'
    main_config: MainConfig
    schemas: dict[str, Schema]

    def __init__(self):
        pass

    def main(self) -> bool:
        with gh.GitHubAction() as gha:
            self.gh = gha
            secret = self.gh.input('VAULT_KEY')
            if not secret:
                raise RuntimeError('VAULT_KEY must be provided')
            self.vault_lib = VaultLib([('', secret)])
            main_config = self.gh.input('CONFIG','.github/secrets-vault/config.yml')
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
        schema = self.parse_schema(env)
        for key, secret in schema.secrets.items():
            if secret.mask:
                self.gh.add_mask(secret.value)
            if secret.env:
                self.gh.set_env(key, secret.value)
            else:
                self.gh.set_output(key, secret.value)


    def parse_schema(self, environment: str) -> Schema:
        filename = f'{self.file_root}/{environment}.yml'
        with open(filename) as f:
            schema_raw = yaml.safe_load(f)
            schema = Schema.parse_raw(schema_raw)
            self.schemas[environment] = schema
            return schema

    def load_secrets(self, schema: Schema):
        vault_file = schema.vault_file
        filename = f'{self.file_root}/{environment}.yml'


def main():
    import sys
    try:
        main = Main()
        if not main.main():
            sys.exit(1)
    except Exception as e:
        sys.exit(2)


if __name__ == "__main__":
    main()
