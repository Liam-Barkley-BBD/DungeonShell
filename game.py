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
            #choose scene
            # scene = game_agent.choose_scene(game_instance, math.floor(math.random() * (len(GameScene)-1)))
            scene = game_agent.create_scene(game_instance, GameScene.COMBAT)
            print(scene.name)
            print("______________________________")
            print(scene)

            # create combat scene based on generated summary and players
            combat_scene = game_agent.get_combat_scene(scene, game_instance.players)
            print("*** Combat scene ***")
            print(combat_scene)
            while True:

                # let each player perform an action
                for i, player in enumerate(game_instance.players):

                    characters = list(filter(lambda character: character.name == player.name, combat_scene.characters))

                    if len(characters) != 1:
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
                            raise ValueError("FUCK")
                        
                    if hit:
                        # TODO: update xp
                        pass
                
                    # get action result
                    action_result = game_agent.get_action_result(combat_scene, player.name, player_response, hit, random.choice(["MINOR", "MEDIOCRE", "EXTREME"]))
                    print("** Outcome ** ")
                    print(action_result.feedback)
                    # update combat scene according to result
                    combat_scene = game_agent.get_updated_combat_scene(combat_scene, action_result.outcome)
                    print(combat_scene)

                # prompt llm to decide if scene is over
                # if over, update the players list to reflect combat scene state

            # ask players to allocate attribute points
            game_instance.iteration += 1
            
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

