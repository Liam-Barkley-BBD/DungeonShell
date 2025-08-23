from agent import GameAgent
from models import *

game_agent = GameAgent()

def main():
    initialise_game()

def initialise_game():
    num_characters = int(input("How many players?\n"))
    story_prompt = input("What theme are we going for?\n")
    players: list[PlayerPrompt] = []
    for i in range(num_characters):
        players.append(PlayerPrompt(input(f"Player {i+1}, Please enter your name"),input(f"Player {i+1}, please enter a description of your character\n")))

    story_summary = game_agent.get_story_summary(story_prompt, players)

    print("The story summary is:")
    print(story_summary)

    # Generate stats for each player based on the descriptions provided and create player objects and add them to the game state
    for player_desc in players:
        player_obj = game_agent.get_player_object(player_desc.name, player_desc.description)
        print(f"Player {player_desc.name} object:\n{player_obj}")

    game = GameState(num_characters=num_characters, story_summary=story_summary)

if __name__ == "__main__":
    main()

