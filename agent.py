import os
from typing import List
from dotenv import load_dotenv
import subprocess

from langchain_openai import ChatOpenAI, custom_tool

from langchain.agents import initialize_agent, AgentType, tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from langgraph.prebuilt import create_react_agent
from prompts import *

from models import *

load_dotenv()

class GameAgent(object):

    def __init__(self):
        self.agent = ChatOpenAI(
                        model="gpt-5",
                        temperature=0,
                        max_tokens=None,
                        timeout=None,
                        max_retries=2,
                        output_version="responses/v1",
                    )
        
    def invoke_agent(self, parser: JsonOutputParser, prompt :str):
        prompt_template = PromptTemplate(
            template=  "Answer the user query\n{format_instructions}\n{query}",
            input_variables=[],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt_template | self.agent | parser
        return chain.invoke({"query": prompt})
        
    def get_story_summary(self, story_prompt: str, players: List[PlayerPrompt]):
        return self.agent.invoke(story_summary_prompt(story_prompt=story_prompt, players=players))
    
    def create_scene(self, game_instance : GameState, scene_type : GameScene) -> SceneDescription:
        parser = JsonOutputParser(pydantic_object=SceneDescription)
        
        match scene_type:
            case GameScene.COMBAT:
                prompt = get_combat_prompt(game_instance)

        return SceneDescription(**self.invoke_agent(parser=parser, prompt=prompt))
            
    def get_combat_scene(self, scene : SceneDescription, players : List[Player]) -> CombatScene:
        parser = JsonOutputParser(pydantic_object=CombatScene)
        prompt = get_combat_scene_prompt(scene, players)
        return CombatScene(**self.invoke_agent(parser=parser, prompt=prompt))
    
    def get_combat_info(self, player_response : str, combat_scene, player : Player) -> Action:
        parser = JsonOutputParser(pydantic_object=Action)
        prompt = get_action(combat_scene, player, player_response)
        result = self.invoke_agent(parser=parser, prompt=prompt)
        print(result)
        return Action(**result)   
    
    def get_player_object(self, player_name, player_description) -> Player:
        parser = JsonOutputParser(pydantic_object=Player)
        prompt = get_player_prompt(player_name, player_description)
        return Player(**self.invoke_agent(parser=parser, prompt=prompt))
    
    def get_action_result(self, combat_scene: CombatScene, actor : str, requested_action: str, action_result: bool, impact: str) -> ActionOutcome:
        parser = JsonOutputParser(pydantic_object=ActionOutcome)
        prompt = get_action_result_prompt(combat_scene, actor, requested_action, action_result, impact)
        result = self.invoke_agent(parser=parser, prompt=prompt)
        print(result)
        return ActionOutcome(**result)   

    def get_updated_combat_scene(self, combat_scene: CombatScene, outcome : str) -> CombatScene:
        parser = JsonOutputParser(pydantic_object=CombatScene)
        prompt = get_updated_combat_scene_prompt(combat_scene, outcome)
        return CombatScene(**self.invoke_agent(parser=parser, prompt=prompt))


# agent = create_react_agent(llm, tools=[], prompt="You are a dungeon master for a text based D&D game.")

# # --- Example Run ---
# if __name__ == "__main__":
#     # user_query = "what branch am I on"
#     # response = agent.run(user_query)
#     # print("\n🤖 Agent Response:\n", response)

#     input_message = {"role": "user", "content": "what branch am I on"}
#     for step in agent.stream(
#         {"messages": [input_message]},
#         stream_mode="values",
#     ):
#         step["messages"][-1].pretty_print()