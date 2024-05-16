from typing import Callable

from pydantic import BaseModel

from secrets.secret import Secret


class Schema(BaseModel):
    name: str | None = None
    parent: str | None = None
    abstract: bool = False
    vault_file: str | None = None
    secrets: dict[str, Secret] = {}


def merge_schema(schema: Schema, current_schema: Schema) -> Schema:
    merged = Schema()
    merged.name = current_schema.name
    merged.secrets = schema.secrets
    for key in set(current_schema.secrets.keys()).union(schema.secrets.keys()):
        if key in schema.secrets:
            if key in current_schema.secrets:
                if schema.secrets[key].final:
                    raise KeyError(f'Secret key {key} declared final in {schema.name} but overridden in {current_schema.name}')
                merged.secrets[key] = current_schema.secrets[key]
                merged.secrets[key].source = current_schema.name
            else:
                merged.secrets[key] = schema.secrets[key]
                merged.secrets[key].source = schema.name
        else:
            merged.secrets[key] = current_schema.secrets[key]
            merged.secrets[key].source = current_schema.name
    return merged


def load_secrets(schema: Schema, current_schema: Schema, data: dict[str,str]) -> None:
    for key in set(schema.secrets.keys()).union(set(data.keys())):
        if key not in schema.secrets:
            raise KeyError(f'Key {key} not found in schema {schema.name}')
        if key in data:
            schema.secrets[key].value = data[key]


def validate_schema(schema: Schema, error) -> bool:
    result = True
    for key, secret in schema.secrets.items():
        if secret.value is None and not secret.optional:
            error(f'Secret key {key} is missing a value in schema {schema.name}')
            result = False
    return result
