import math
import random
from agent import GameAgent
from models import *

game_agent = GameAgent()

def main():
    game_instance = initialise_game()
    num_scenes = 10

    # game loop
    while(True):
        for i in range(num_scenes):
            scene = game_agent.create_scene(game_instance, GameScene.COMBAT)
            print(scene.name)
            print("______________________________")
            print(scene)

            # create combat scene based on generated summary and players
            combat_scene = game_agent.get_combat_scene(scene, game_instance.players)
            print("*** Combat scene ***")
            print(combat_scene)
            is_running = True
            while is_running:

                # let each player perform an action
                for i, player in enumerate(game_instance.players):

                    characters = list(filter(lambda character: character.name == player.name, combat_scene.characters))

                    if len(characters) != 1:
                        continue
                    elif not characters[0].current_hp > 0:
                        continue

                    print("*** Player ***")
                    print(player)
                    player_response = input(f"How do you respond?")
                    action : ActionOutcome = game_agent.get_combat_info(player_response, combat_scene, player)
                    print(action)
                    # calculate hit or miss and update xp
                    match action.attribute:
                        case "STRENGTH":
                            hit = action.difficultyClass <= player.strength + random.randint(1,20)
                        case "CHARISMA":
                            hit = action.difficultyClass <= player.charisma + random.randint(1,20)
                        case "INTELLIGENCE":
                            hit = action.difficultyClass <= player.intelligence + random.randint(1,20)
                        case _:
                            raise ValueError("Unknown attribute provided")
                    
                    choices = ["MINOR", "MEDIOCRE", "EXTREME"]
                    random_index = random.randint(0,2)
                    action_modifier = choices[random_index]
                    if hit:
                        player.xp +=  (random_index + 1)              
                    
                    # get action result
                    action_result = game_agent.get_action_result(combat_scene, player.name, player_response, hit, action_modifier)
                    print("** Outcome ** ")
                    print(action_result.feedback)
                    # update combat scene according to result
                    combat_scene = game_agent.get_updated_combat_scene(combat_scene, action_result.outcome)
                    print(combat_scene)

                    # Now that the combat scene state has potentially shifted we need to reconcile them now
                    reconcile_player_hp(combat_scene, game_instance)
                    is_running = False

                    #TODO (CADE): update player state

                # TODO (LIAM): prompt llm to decide if scene is over
                    

                # TODO (CADE): if over, update the players list to reflect combat scene state

            # ask players to allocate attribute points
            print("** The scene has ended **")
            for i, player in enumerate(game_instance.players):
                available_levels = player.xp//10
                print(f"Player {i+1}", f"You have {player.xp} experience points.")
                if available_levels > 0:
                    print(f"You can level up one of your attributes by {available_levels} levels")
                    choice = None
                    while(choice == None):
                        potential_choice = input("Choose one of the following options:\n*Strength(1)\n*Intelligence(2)\n*Charisma(3)\n")
                        try:
                            if int(potential_choice) in [1,2,3]:
                                choice = potential_choice
                        except:
                            continue

                    match choice:
                        case 1:
                            player.strength += available_levels
                        case 2:
                            player.intelligence += available_levels
                        case 3:
                            player.charisma += available_levels
                    
                    # set the xp on the player to be whatever is left over
                    player.xp = player.xp%10
            game_instance.iteration += 1

def reconcile_player_hp(combat_scene : CombatScene, game_instance : GameState):
    removal_indices = []
    for i, player in enumerate(game_instance.players):
        if player.name not in [character.name for character in combat_scene.characters]:
            removal_indices.append(i)
            continue

        # Get the corresponding character in the combat scene
        character = list(filter(lambda c:c.name == player.name, combat_scene.characters))[0]
        player.current_hp = character.current_hp
    




def initialise_game():
    num_characters = int(input("How many players?\n"))
    story_prompt = input("What theme are we going for?\n")
    players: list[PlayerPrompt] = []
    for i in range(num_characters):
        players.append(PlayerPrompt(input(f"Player {i+1}, Please enter your name\n"),input(f"Player {i+1}, please enter a description of your character\n")))

    story_summary = game_agent.get_story_summary(story_prompt, players)
    player_objs = []

    print("**The dungeon master explains the story arc**")
    print(story_summary.content[1]['text'])

    # Generate stats for each player based on the descriptions provided and create player objects and add them to the game state
    print("**The Heroes ...**")
    for i, player in enumerate(players):
        player_obj: Player = game_agent.get_player_object(player.name, player.description)
        player_objs.append(player_obj)
        print(f"Player {i+1}")
        print("_______________________________________")
        print(str(player_obj))
        
    print(type(player_objs))
    return GameState(num_characters=num_characters, story_summary=story_summary, players=player_objs, game_summary="Nothing has happened", iteration=1)


if __name__ == "__main__":
    main()

