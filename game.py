from agent import GameAgent
from models import *
import rich as r
import rich.align as ra
import rich.console as rcon
import rich.columns as rc
import rich.prompt as rpr
import ascii_image
import ansi
import asyncio
import aiohttp
import random

game_agent = GameAgent()

def show_loading():
    r.print(ra.Align.center('[blink]Loading...'), end='')

def clear_loading():
    ansi.move_up()
    ansi.erase_line()

async def main():
    game_instance = await initialise_game()
    num_scenes = 10

    # game loop
    while(True):
        for _ in range(num_scenes):
            show_loading()
            scene = await game_agent.create_scene(game_instance, GameScene.COMBAT)
            clear_loading()
            
            r.print(f"\n[cyan]{scene.name}\n")
            
            for word in scene.description.split():
                print(f"{word} ", end='', flush=True)
                await asyncio.sleep(0.02)
            
            print('\n')

            show_loading()
            combat_scene = await game_agent.get_combat_scene(scene, game_instance.players)
            clear_loading()

            r.print(rpanel.Panel(
                rc.Columns(
                    [character.tiny() for character in combat_scene.characters],
                    padding=(1, 2)
                ),
                title="Character Stats"
            ))
            
            while True:
                # let each player perform an action
                for player in game_instance.players:
                    characters = list(filter(lambda character: character.name == player.name, combat_scene.characters))

                    if len(characters) != 1:
                        continue

                    print()
                    r.print(player.medium_without_name(f"[cyan]{player.name}[/]'s Turn"))
                    print()
                    
                    r.print(f"What do you do? ", end='')
                    player_response = input()
                    
                    action = await game_agent.get_combat_info(player_response, combat_scene, player)

                    r.print(f"[gray37]Difficulty:[/] [yellow]{action.attribute}[/] {action.difficultyClass}\n")
                    
                    # calculate hit or miss and update xp
                    match action.attribute:
                        case "STRENGTH":
                            hit = action.difficultyClass <= player.strength + random.randint(1,20)
                        case "CHARISMA":
                            hit = action.difficultyClass <= player.charisma + random.randint(1,20)
                        case "INTELLIGENCE":
                            hit = action.difficultyClass <= player.intelligence + random.randint(1,20)
                        case _:
                            hit = False
                        
                    if hit:
                        # TODO: update xp
                        pass
                
                    show_loading()
                    action_result = await game_agent.get_action_result(combat_scene, player.name, player_response, hit, random.choice(["MINOR", "MEDIOCRE", "EXTREME"]))
                    clear_loading()
                    
                    r.print(f"{action_result.feedback} [gray37]{action_result.outcome}[/]\n")
                    
                    show_loading()
                    combat_scene = await game_agent.get_updated_combat_scene(combat_scene, action_result.outcome)
                    clear_loading()

                    r.print(rpanel.Panel(
                        rc.Columns(
                            [character.tiny() for character in combat_scene.characters],
                            padding=(1, 2)
                        ),
                        title="Character Stats"
                    ))

                # prompt llm to decide if scene is over
                # if over, update the players list to reflect combat scene state

            # ask players to allocate attribute points
            game_instance.iteration += 1

async def initialise_game():
    num_characters = None

    while not isinstance(num_characters, int):
        try:
            num_characters = int(rpr.Prompt.ask("[cyan]How many players?").strip())
            if num_characters == 0:
                print("Cannot play with 0 players!")
                num_characters = None
        except ValueError:
            pass

    story_prompt = ""
    
    while len(story_prompt) == 0:
        story_prompt = rpr.Prompt.ask("[cyan]What theme are we going for?").strip()
    
    player_prompts: list[PlayerPrompt] = []
    for i in range(num_characters):
        r.print(f"\n[bold magenta]==== PLAYER {i+1} ====")
        name = ""
        while len(name) == 0:
            name = rpr.Prompt.ask(f"[cyan]Chracter name").strip()
        desc = ""
        while len(desc) == 0:
            desc = rpr.Prompt.ask(f"[cyan]Character descripton").strip()
        player_prompts.append(PlayerPrompt(name, desc))

    session = aiohttp.ClientSession()
    player_tasks = map(lambda prompt: game_agent.get_player_object(session, prompt.name, prompt.description), player_prompts)

    print()
    r.print(f"[bold blue]{ascii_image.WIZARD}[/bold blue]")
    
    ansi.move_up(ascii_image.WIZARD_H)
    ansi.move_to_col(ascii_image.WIZARD_W + 2)

    story_summary = ""

    line_max_width = ansi.TERM_SIZE.columns - ascii_image.WIZARD_W - 16
    line_width = 0
    line_count = 0
    
    async for chunk in game_agent.get_story_summary_streamed(story_prompt, player_prompts):
        chunk_text = chunk.text()
        story_summary += chunk_text
        
        line_width += len(chunk_text)
        if line_width > line_max_width:
            print()
            ansi.move_to_col(ascii_image.WIZARD_W + 2)
            line_width = 0
            line_count += 1
            chunk_text = chunk_text.lstrip()
        
        print(chunk_text, end='', flush=True)
    
    for _ in range(ascii_image.WIZARD_H - line_count + 1):
        print()
    
    show_loading()
    
    players = await asyncio.gather(*player_tasks)
    await session.close()

    clear_loading()

    for player in players:
        r.print(player.large())
        await asyncio.sleep(1)

    return GameState(num_characters, story_summary, players)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except EOFError:
        print("\n\nExiting...")
    except Exception as ex:
        r.print(f"\n\n[red]An error has occurred.\n\n")
        raise
