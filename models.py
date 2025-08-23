from typing import List
from pydantic import BaseModel, Field
from dataclasses import dataclass
import rich.columns as rc
import rich.panel as rpanel
from ascii_image import AsciiMipmaps

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
    current_hp : int = Field(description="current hp")
    max_hp : int = Field(description=" maximum hp")
    strength : int = Field(description="strength level")
    intelligence : int = Field(description="inteligence level")
    charisma : int = Field(description="charisma level")
    inventory: List[str] = Field(description="Player items")

    def hp_bar(self):
        hp = self.current_hp
        return progress(hp, self.max_hp, hp < self.max_hp / 3 and hp > 0)

    def tiny(self):
        inventory_str = ", ".join(self.inventory) if len(self.inventory) > 0 else "Empty"
        dead = self.current_hp == 0

        return f"""[{ "strike " if dead else "" }cyan]{self.name} (Level {self.level})[/]{" [red]DEAD[/]" if dead else ""}
[yellow]HEALTH[/] {self.hp_bar()} {self.current_hp} / {self.max_hp}
[cyan]ITEMS[/]  {inventory_str}"""

    def small(self):
        inventory_str = "\n".join(map(lambda i: f"• {i}", self.inventory)) if len(self.inventory) > 0 else "Empty"
        dead = self.current_hp == 0

        return rpanel.Panel(
            rc.Columns([
                f"\n{self.image.small}",
                f"""
[{ "strike " if dead else "" }cyan]{self.name} (Level {self.level})[/]{" [red]DEAD[/]" if dead else ""}

[yellow]HEALTH[/] {self.hp_bar()} {self.current_hp} / {self.max_hp}

[red]STRENGTH[/] {self.strength}    [blue]INTELLIGENCE[/] {self.intelligence}    [magenta]CHARISMA[/] {self.charisma}

[cyan]ITEMS[/]
{inventory_str}
""",
            ]),
        )

    def medium(self):
        inventory_str = "\n".join(map(lambda i: f"• {i}", self.inventory)) if len(self.inventory) > 0 else "Empty"
        dead = self.current_hp == 0

        return rpanel.Panel(
            rc.Columns([
                f"\n{self.image.medium}",
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

class GameState(object):
    def __init__(self, num_characters: int, story_summary: str, players: List[Player]):
        self.num_characters = num_characters
        self.story_summary = story_summary
        self.players = players