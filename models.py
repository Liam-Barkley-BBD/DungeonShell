from typing import List
from pydantic import BaseModel, Field
from dataclasses import dataclass
import rich.columns as rc
import rich.panel as rpanel
from ascii_image import AsciiMipmaps
from enum import Enum

def progress(current: float, max: float, blink: bool = False):
    char = '━'

    current_int = int(current)
    max_int = int(max)

    bar = ""
    if current == 0:
        bar = f"[red]{char * max_int}[/red]"
    elif current_int == 0:
        bar = f"[green]╸[/green][red]{char * (max_int-1)}[/red]"
    elif current == max:
        bar = f"[green]{char * max_int}[/green]"
    elif current_int == max_int:
        bar = f"[green]{char * max_int}[/green][red]╺[/red]"
    else:
        bar = f"[green]{char * current_int}[/green][red]╺{char * (max_int - current_int - 1)}[/red]"
    
    if blink:
        bar = f"[blink]{bar}[/blink]"
    
    return bar

@dataclass
class PlayerPrompt:
    name: str
    description: str

class Player(BaseModel):
    name: str = Field(description="name")
    image: AsciiMipmaps | None = Field(description="image should be null")
    level: int = Field(description="level")
    current_hp: int = Field(description="current hp")
    max_hp: int = Field(description=" maximum hp")
    strength: int = Field(description="strength level")
    intelligence: int = Field(description="inteligence level")
    charisma: int = Field(description="charisma level")
    inventory: List[str] = Field(description="Player items")

    def hp_bar(self):
        hp = self.current_hp
        return progress(hp, self.max_hp, hp < self.max_hp / 3 and hp > 0)

    def small_without_name(self):
        inventory_str = ", ".join(self.inventory) if len(self.inventory) > 0 else "Empty"

        return f"""[yellow]HEALTH[/] {self.hp_bar()} {self.current_hp} / {self.max_hp}
[cyan]ITEMS[/]  {inventory_str}"""

    def small(self):
        inventory_str = ", ".join(self.inventory) if len(self.inventory) > 0 else "Empty"
        dead = self.current_hp == 0

        return f"""[{ "strike " if dead else "" }cyan]{self.name} (Level {self.level})[/]{" [red]DEAD[/]" if dead else ""}
[yellow]HEALTH[/] {self.hp_bar()} {self.current_hp} / {self.max_hp}
[cyan]ITEMS[/]  {inventory_str}"""

    def medium(self):
        inventory_str = "\n".join(map(lambda i: f"• {i}", self.inventory)) if len(self.inventory) > 0 else "Empty"
        dead = self.current_hp == 0

        return rpanel.Panel(
            rc.Columns([
                f"\n{self.image.small if self.image is not None else ''}",
                f"""
[{ "strike " if dead else "" }cyan]{self.name} (Level {self.level})[/]{" [red]DEAD[/]" if dead else ""}

[yellow]HEALTH[/] {self.hp_bar()} {self.current_hp} / {self.max_hp}

[red]STRENGTH[/] {self.strength}    [blue]INTELLIGENCE[/] {self.intelligence}    [magenta]CHARISMA[/] {self.charisma}

[cyan]ITEMS[/]
{inventory_str}
""",
            ]),
        )

    def large(self):
        inventory_str = "\n".join(map(lambda i: f"• {i}", self.inventory)) if len(self.inventory) > 0 else "Empty"
        dead = self.current_hp == 0

        return rpanel.Panel(
            rc.Columns([
                f"\n{self.image.medium if self.image is not None else ''}",
                f"""
[{ "strike " if dead else "" }cyan]{self.name} (Level {self.level})[/]{" [red]DEAD[/]" if dead else ""}

[yellow]HEALTH[/] {self.hp_bar()} {self.current_hp} / {self.max_hp}

[red]STRENGTH[/]     {self.strength}
[blue]INTELLIGENCE[/] {self.intelligence}
[magenta]CHARISMA[/]     {self.charisma}

[cyan]ITEMS[/]
{inventory_str}
""",
            ]),
        )

@dataclass
class GameState(object):
    num_characters: int
    story_summary: str
    players: list[Player]
    game_summary: str = "Nothing has happened"
    iteration: int = 1

class GameScene(Enum):
    COMBAT = 0
    EXPLORATION = 1
    SOCIAL = 2

class Action(BaseModel):
    difficultyClass: int = Field("The difficulty class of the action")
    attribute: str = Field("'The attribute corresponding to this action'")
   
class Character(BaseModel):
    name: str = Field(description="Name")
    current_hp: int = Field(description="Current HP")
    max_hp: int = Field(description="Max HP")
    type: str = Field(description="'PLAYER' or 'ENEMY'")

    def hp_bar(self):
        hp = self.current_hp
        return progress(hp, self.max_hp, hp < self.max_hp / 3 and hp > 0)

    def tiny(self):
        dead = self.current_hp == 0
        return f"""[{ "strike " if dead else "" }cyan]{self.name}[/]{" [red]DEAD[/]" if dead else ""}
[yellow]HEALTH[/] {self.hp_bar()} {self.current_hp} / {self.max_hp}"""

class CombatScene(BaseModel):
    characters: list[Character]
    battle_summary: str

class ActionOutcome(BaseModel):
    feedback: str = Field("Feedback to give player in game")
    outcome: str = Field("How action influenced the game state")

class SceneDescription(BaseModel):
    name: str = Field("Name of scene")
    description: str = Field("Scene description")
