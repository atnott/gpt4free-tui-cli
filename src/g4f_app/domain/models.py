from dataclasses import dataclass

@dataclass
class Message:
    role: str
    content: str

@dataclass
class ProviderStatus:
    name: str
    is_working: bool