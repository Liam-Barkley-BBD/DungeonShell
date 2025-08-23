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
        
    def get_story_summary(self, story_prompt: str, players: List[PlayerPrompt]):
        return self.agent.invoke(story_summary_prompt(story_prompt=story_prompt, players=players))
    
    def get_player_object(self, player_name, player_description):
        parser = JsonOutputParser(pydantic_object=Player)
        prompt = get_player_prompt(player_name, player_description)

        prompt_template = PromptTemplate(
            template= prompt + "Answer the user query\n{format_instructions}",
            input_variables=["player_description"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt_template | self.agent | parser
        return chain.invoke({"query": prompt})

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