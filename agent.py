import aiohttp
import asyncio

from typing import List
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, custom_tool

from langchain.agents import initialize_agent, AgentType, tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from langgraph.prebuilt import create_react_agent
from prompts import *

from models import *

import ascii_image

load_dotenv()

class GameAgent(object):
    def __init__(self):
        self.agent = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            output_version="responses/v1",
        )
        
    def get_story_summary_streamed(self, story_prompt: str, players: List[PlayerPrompt]):
        return self.agent.astream(story_summary_prompt(story_prompt=story_prompt, players=players))
    
    async def invoke_agent(self, parser: JsonOutputParser, prompt :str):
        prompt_template = PromptTemplate(
            template=  "Answer the user query\n{format_instructions}\n{query}",
            input_variables=[],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt_template | self.agent | parser
        return await chain.ainvoke({"query": prompt})

    async def create_scene(self, game_instance: GameState, scene_type: GameScene) -> SceneDescription:
        parser = JsonOutputParser(pydantic_object=SceneDescription)
        
        match scene_type:
            case GameScene.COMBAT:
                prompt = get_combat_prompt(game_instance)

        scene = await self.invoke_agent(parser=parser, prompt=prompt)
        
        return SceneDescription(**scene)
    
    async def get_combat_scene(self, scene: SceneDescription, players: list[Player]) -> CombatScene:
        parser = JsonOutputParser(pydantic_object=CombatScene)
        prompt = get_combat_scene_prompt(scene, players)
        scene = await self.invoke_agent(parser=parser, prompt=prompt)
        return CombatScene(**scene)
    
    async def get_combat_info(self, player_response: str, combat_scene: CombatScene, player: Player) -> Action:
        parser = JsonOutputParser(pydantic_object=Action)
        prompt = get_action(combat_scene, player, player_response)
        result = await self.invoke_agent(parser=parser, prompt=prompt)
        return Action(**result)   
    
    async def get_player_object(self, session: aiohttp.ClientSession, player_name: str, player_description: str) -> Player:
        parser = JsonOutputParser(pydantic_object=Player)
        prompt = get_player_prompt(player_name, player_description)
        
        response = self.invoke_agent(parser=parser, prompt=prompt)
        image = ascii_image.generate_ascii_image(session, f"{player_name}, {player_description}, STANCE FACING CAMERA, WHITE BACKGROUND")
        
        [response, image] = await asyncio.gather(response, image)
        
        player = Player(**response)
        player.image = image
        
        return player
    
    async def get_action_result(self, combat_scene: CombatScene, actor: str, requested_action: str, action_result: bool, impact: str) -> ActionOutcome:
        parser = JsonOutputParser(pydantic_object=ActionOutcome)
        prompt = get_action_result_prompt(combat_scene, actor, requested_action, action_result, impact)
        result = await self.invoke_agent(parser=parser, prompt=prompt)
        return ActionOutcome(**result)   

    async def get_updated_combat_scene(self, combat_scene: CombatScene, outcome: str) -> CombatScene:
        parser = JsonOutputParser(pydantic_object=CombatScene)
        prompt = get_updated_combat_scene_prompt(combat_scene, outcome)
        scene = await self.invoke_agent(parser=parser, prompt=prompt)
        return CombatScene(**scene)
