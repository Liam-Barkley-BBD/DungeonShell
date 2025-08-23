from typing import List
from pydantic import BaseModel, Field

class GameState(object):
    def __init__(self, num_characters, story_summary, players):
        self.num_characters = num_characters
        self.story_summary = story_summary
        self.players = players

class PlayerPrompt(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Player(BaseModel):
    name: str = Field(description="name")
    level: int = Field(description="level")
    current_hp : int = Field(description="current hp")
    max_hp : int = Field(description=" maximum hp")
    strength : int = Field(description="strength level")
    intelligence : int = Field(description="inteligence level")
    charisma : int = Field(description="charisma level")
    inventory: List[str] = Field(description="Player items")



