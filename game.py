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
        players.append(PlayerPrompt(input(f"Player {i+1}, Please enter your name\n"),input(f"Player {i+1}, please enter a description of your character\n")))

    story_summary = game_agent.get_story_summary(story_prompt, players)
    player_objs = []

    print("**The dungeon master explains the story arc**")
    print(story_summary.content[1]['text'])

    # Generate stats for each player based on the descriptions provided and create player objects and add them to the game state
    print("**The Heroes ...**")
    for i, player in enumerate(players):
        player_obj: Player = Player(**game_agent.get_player_object(player.name, player.description))
        player_objs.append(player_obj)
        print(f"Player {i+1}")
        print("_______________________________________")
        print(str(player_obj))

    game = GameState(num_characters=num_characters, story_summary=story_summary, players=player_objs)

if __name__ == "__main__":
    main()

