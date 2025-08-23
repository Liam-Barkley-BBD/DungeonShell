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

game_agent = GameAgent()

async def main():
    await initialise_game()

async def initialise_game():
    num_characters = None

    while not isinstance(num_characters, int):
        try:
            num_characters = int(rpr.Prompt.ask("[cyan]How many players?").strip())
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
    
    r.print(ra.Align.center('[blink]Loading...'), end='')
    
    players = await asyncio.gather(*player_tasks)
    await session.close()

    ansi.move_up()
    ansi.erase_line()

    for player in players:
        r.print(player.medium())
        await asyncio.sleep(1)

    for player in players:
        print()
        r.print(player.small())

    for player in players:
        print()
        r.print(player.tiny())
    
    # print()
    
    game = GameState(num_characters=num_characters, story_summary=story_summary, players=players)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except EOFError:
        print("\n\nExiting...")
    except:
        print("\n\nAn error has occurred.")
