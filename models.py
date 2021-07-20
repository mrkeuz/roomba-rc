from dataclasses import dataclass


@dataclass
class Move:
    speed: float
    turn_deg: float


@dataclass
class Server:
    server: str
    port: int
