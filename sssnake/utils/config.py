from dataclasses import dataclass

@dataclass (frozen=True)
class GameConfig:
    title: str = "Sssnake"


GAMECONFIG = GameConfig()