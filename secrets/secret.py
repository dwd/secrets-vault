from pydantic import BaseModel


class Secret(BaseModel):
    description: str
    mask: bool = True
    env: bool = False
    output_file: str | None = None
    input_file: str | None = None
    optional: bool = False
    final: bool = False
    value: str | None = None
    source: str | None = None
