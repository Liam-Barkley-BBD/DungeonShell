from typing import List
from pydantic import BaseModel, Field

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

    def __str__(self) -> str:
        # ANSI color codes
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        MAGENTA = "\033[95m"
        CYAN = "\033[96m"
        RESET = "\033[0m"
        BOLD = "\033[1m"

        # HP bar
        bar_length = 20
        hp_ratio = self.current_hp / self.max_hp
        filled_length = int(bar_length * hp_ratio)
        empty_length = bar_length - filled_length
        hp_bar = f"{GREEN}{'█' * filled_length}{RED}{'█' * empty_length}{RESET}"

        # Inventory
        inventory_str = ", ".join(self.inventory) if self.inventory else "Empty"

        return (
            f"{BOLD}{CYAN}Player: {self.name} (Level {self.level}){RESET}\n"
            f"HP: [{hp_bar}] {self.current_hp}/{self.max_hp}\n"
            f"{YELLOW}Stats:{RESET}\n"
            f"  {RED}Strength:{RESET}     {self.strength}\n"
            f"  {BLUE}Intelligence:{RESET} {self.intelligence}\n"
            f"  {MAGENTA}Charisma:{RESET}    {self.charisma}\n"
            f"{CYAN}Inventory:{RESET} {inventory_str}"
        )


class GameState(object):
    def __init__(self, num_characters: int, story_summary: str, players: List[Player]):
        self.num_characters = num_characters
        self.story_summary = story_summary
        self.players = players