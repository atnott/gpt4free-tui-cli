from dataclasses import dataclass
from typing import List

@dataclass
class Message:
    role: str
    content: str

@dataclass
class ProviderStatus:
    name: str
    is_working: bool
    supported_models: List[str]
