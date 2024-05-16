from pydantic import BaseModel


class MainConfig(BaseModel):
    environments: list[str] = ['main']
