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
{game_instance.story_summary.content[1]['text']}

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

For the battle summary, briefly capture the context and end the summary with some action the first player needs to respond to.

Scene description: 
{scene.description}

List of players (make sure the names match exactly in your response):
{[p.model_dump_json() for p in players]}

"""

def get_action(combat_scene: CombatScene, player : Player, player_response : str):
    return f"""
Please provide the information need to perform a dungeons and dragons dice roll.

Current game information: 
{combat_scene.model_dump_json()}

Player requesting actions:
{player.model_dump_json()}

Requested action:
{player_response}

Please select the single most applicable attribute required for the requested action: ['STRENGTH', 'INTELLIGENCE', 'CHARISMA']

The difficulty class (DC), should take into account the player's stats. 

If the request is logical and aligns with their stats then the DC should be low (5-10). 

If it is a risky action that could be possible with moderate likelihood then DC should be between 10 and 15.

For very unlikely requests it should be between 15 and 20. 

Finally, for nonsensical requests like using an item not in the players inventory or a request that does not match the narrative, 
you can make the DC 50 to indicate an impossible action.

"""

def get_action_result_prompt(combat_scene: CombatScene, actor : str, requested_action: str, action_result: bool, impact: str):
    return f"""
You are a dungeon master for a D&D game and must a narrative outcome for the following dice roll (≤15 words).

Additionally, you must provide an explicit change to game state, for example 'player Bob loses 10HP':
{combat_scene}

Actor "{actor}" attempted to do the following:
{requested_action}

The die roll resulted in a {"success" if action_result else "failure"} with {impact} impact.

MINOR: 1-3 points
MEDIOCRE: 4-9 points
EXTREME: 10-20 points

"""  

def get_updated_combat_scene_prompt(combat_scene: CombatScene, outcome: ActionOutcome, next_player:str):
    return f"""
Current scene context:
{combat_scene}

Please update the game state according the following changes:
{outcome.game_update}

Update each chatacters health accordingly. If a player has died or fleed the scene then DO NOT include them in the updated list of characters.

Please revise the game summary according to the below update (keeping vital information):
{outcome.outcome}

Finally, please include a new event that '{next_player}' has to respond to unless they are dead in which case give a generic event.

However, only add a new event if it does not seem like the scene is coming to a close to prevent it from dragging on.
"""

def check_scene_termination_prompt(combat_scene: CombatScene):
    return f"""
As D&D dungeon master, it is your duty to determine whether to move onto the next scene.

Based on the context below, please determine whether the scene is complete.

The scene should be complete if for example all enemies or all players have reached 0 HP or if the enemies are no longer hostile.

Note that players may have fleed, so if there are no characters of type "PLAYER" then the scene should also end.

If the scene continues then set 'terminate_reason' to the empty string.

Current scene context:
{combat_scene}

"""
# Adapt the combat scene as necesarry, for example if a player died or fleed, remove them from the list.