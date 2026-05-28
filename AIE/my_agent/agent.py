import os
import sys
from google.adk.agents.llm_agent import Agent

# Dynamically add the current script's directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tools import time_assistant_tools
"""A lonely agent with a single tool"""

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="Tells the current time in a specified city.",
    instruction="You are a helpful assistant that tells the current time in cities. Use the 'get_current_time' tool for this purpose.",
    tools=time_assistant_tools,
)
