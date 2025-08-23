from models import *
from typing import List
import json

def story_summary_prompt(story_prompt: str, players: List[PlayerPrompt]):
    return f"""
Please make an overarching storyline for a D&D game in 100 words or less based on the below.
Theme: {story_prompt}
Player info: 
{json.dumps([player.__dict__ for player in players])}
"""

def get_player_prompt(player_name: str, player_description: str):
    return f"""
Please initialize the player to level 1 and allocate 7 points across each skill attribute according to the players description.

Add inferred inventory items from the player description as singular nouns (≤3 words) representing concrete objects.
    
Please set the health to a value between 10 and 20 based on the inferred physical prowess of the player.

Player name: {player_name}
Player description:
{player_description}

"""