import math
import random
from models import *
from typing import List
import json

def story_summary_prompt(story_prompt: str, players: List[PlayerPrompt]):
    return f"""
Please make an overarching storyline for a D&D game in 100 words or less based on the below.

Keep the plot general enough so that the story has room to grow.

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

def get_combat_prompt(game_instance: GameState):
    num_enemies = random.randint(1, math.ceil(len(game_instance.players) * 1.5))
    return f"""
You must create a dungeons and dragons combat scene describing the enemies that the players below are facing (≤50 words).

Players:
{[p.model_dump_json() for p in game_instance.players]}

Storyline:
{game_instance.story_summary}

Game history:
{game_instance.game_summary}

The story must come to a conclusion {"in " + (str(10 - game_instance.iteration) + " scenes from now") if (10 - game_instance.iteration) else "during play of this scene"}.

You must describe {f"{num_enemies} enemies" if num_enemies > 1 else "one enemy"}.
"""

def get_combat_scene_prompt(scene: SceneDescription, players: List[Player]):
    return f"""
Please initialize a dungeons and dragons fighting scenario according to the required format.

Initialize all players health according to the below. 

Initialize the enemies health inferred from the scene description and scaled to give the players a fair chance.

Scene description: 
{scene.description}

List of players (make sure the names match exactly in your response):
{[p.model_dump_json() for p in players]}

"""

def get_action(combat_scene: CombatScene, player: Player, player_response: str):
    return f"""
Please provide the information need to perform a dungeons and dragons dice roll using a 20 sided die.

Current game information: 
{combat_scene.model_dump_json()}

Requested action:
{player_response}

Player requesting actions:
{player.model_dump_json()}

Please select the single most applicable attribute required for the requested action: ['STRENGTH', 'INTELLIGENCE', 'CHARISMA']

"""

def get_action_result_prompt(combat_scene: CombatScene, actor: str, requested_action: str, action_result: bool, impact: str):
    return f"""
You are a dungeon master for a D&D game and must provide player feedback for the following dice roll (≤15 words).

Additionally, you must provide an explicit outcome describing how the following context should be updated, for example 'player Bob loses 10HP':
{combat_scene}

Actor "{actor}" attempted to do the following:
{requested_action}

The die roll resulted in a {"success" if action_result else "failure"} with {impact} impact.
"""  

def get_updated_combat_scene_prompt(combat_scene: CombatScene, outcome: str):
    return f"""
Please provide an updated combat scene model for the below.

Current scene context:
{combat_scene}

Please update the combat scene according the following outcome:
{outcome}

Please update the character list and their health accordingly. 

For example, if a player has died or fleed the scene they need to be removed from the list of characters.

Finally, please revise the game summary to provide a narrative retelling of what has happened in the scene so far and include the new information.
"""

# Adapt the combat scene as necesarry, for example if a player died or fleed, remove them from the list.