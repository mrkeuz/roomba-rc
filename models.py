from dataclasses import dataclass


@dataclass
class MoveModel:
    speed: float
    turn_deg: float


@dataclass
class ServerModel:
    server: str
    port: int
