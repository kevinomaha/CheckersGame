from dataclasses import dataclass
from typing import Dict

@dataclass
class Environment:
    name: str
    domain_name: str = None
    certificate_arn: str = None

class Config:
    DEV = Environment(
        name="dev",
    )
    
    PROD = Environment(
        name="prod",
    )

    @staticmethod
    def get_env_config(env_name: str) -> Environment:
        return getattr(Config, env_name.upper())
