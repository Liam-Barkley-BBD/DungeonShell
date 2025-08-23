from agent import GameAgent
from models import *
import rich as r
import rich.align as ra
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
    num_scenes = 5

    # game loop
    for scene_index in range(num_scenes):
        show_loading()
        scene = await game_agent.create_scene(game_instance, GameScene.COMBAT, scene_index, num_scenes)
        clear_loading()
        
        r.print(f"\n[cyan]{scene.name}\n")
        print(scene.description)
        print()

        show_loading()
        combat_scene = await game_agent.initialize_combat_scene(scene, game_instance.players)
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
            for i, character in enumerate(combat_scene.characters):
                if character.type != "PLAYER" or character.current_hp <= 0:
                    continue

                [player] = list(filter(lambda player: character.name == player.name, game_instance.players))

                await asyncio.sleep(2.5)
                
                print()
                r.print(player.medium_without_name(f"[cyan]{player.name}[/]'s Turn"))
                print()

                show_loading()                
                event = await game_agent.get_next_event(combat_scene, player.name)
                clear_loading()
                print(event.event)
                print()
                
                r.print(f"What do you do? ", end='')
                player_response = input()
                
                action = await game_agent.get_combat_info(player_response, combat_scene, player, event.event)

                dice_roll = random.randint(1,20)
                attribute_score = 0
                
                # calculate hit or miss and update xp
                match action.attribute:
                    case "STRENGTH":
                        attribute_score = player.strength
                    case "CHARISMA":
                        attribute_score = player.charisma
                    case "INTELLIGENCE":
                        attribute_score = player.intelligence
                    case other:
                        print(f"Unknown attribute {other}, defaulting to strength")
                        action.attribute = "STRENGTH"
                        attribute_score = player.strength
                
                hit = action.difficultyClass <= attribute_score + dice_roll

                r.print(f"[gray37]Difficulty:[/] [yellow]{action.attribute}[/] {action.difficultyClass}")
                r.print(f"[gray37]Dice Roll:[/] {attribute_score} (Player [yellow]{action.attribute}[/]) + {dice_roll} ([yellow]DICE[/]) {">=" if hit else "<"} {action.difficultyClass}")

                hit_diff = abs(attribute_score + dice_roll - action.difficultyClass)
                
                if hit_diff < 3:
                    action_modifier = "MINOR"
                elif hit_diff < 10:
                    action_modifier = "MEDIOCRE"
                else:
                    action_modifier = "EXTREME"
                
                action_modifier_text = action_modifier[0] + action_modifier[1:].lower()
                
                r.print(f"[green]{action_modifier_text} success![/]" if hit else f"[red]{action_modifier_text} failure[/]")
                print()
                
                if hit:
                    player.xp += hit_diff + 1
                
                show_loading()
                action_result = await game_agent.get_action_result(combat_scene, player.name, player_response, hit, action_modifier)
                clear_loading()
                
                print(f"{action_result.outcome}\n")
                
                # update combat scene according to result
                player_characters = list(filter(lambda character: character.type == "PLAYER", combat_scene.characters))

                for i, player_character in enumerate(player_characters):
                    if player_character.name == player.name:
                        curr_player_idx = i
                        break

                next_player = player_characters[(curr_player_idx + 1) % (len(player_characters))].name
                show_loading()
                combat_scene = await game_agent.get_updated_combat_scene(combat_scene, action_result, next_player)
                clear_loading()

                r.print(rpanel.Panel(
                    rc.Columns(
                        [character.tiny() for character in combat_scene.characters],
                        padding=(1, 2)
                    ),
                    title="Character Stats"
                ))

                reconcile_player_hp(combat_scene, game_instance)
            
            show_loading()
            check_termination = await game_agent.check_scene_termination(combat_scene)
            clear_loading()

            if check_termination.terminate_scene:
                r.print(check_termination.terminate_reason)
                break

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
                player.xp = player.xp % 10
        
        show_loading()
        updated_summary = await game_agent.get_updated_game_history(game_instance.game_summary, combat_scene.battle_summary)
        clear_loading()
        game_instance.game_summary = updated_summary



def reconcile_player_hp(combat_scene: CombatScene, game_instance: GameState):
    removal_indices = []

    for i, player in enumerate(game_instance.players):
        if player.name not in [character.name for character in combat_scene.characters]:
            removal_indices.append(i)
            continue

        # Get the corresponding character in the combat scene
        character = list(filter(lambda c:c.name == player.name, combat_scene.characters))[0]
        player.current_hp = character.current_hp

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

    print()
    r.print(ra.Align.center("[yellow bold]Players[/]"))

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
