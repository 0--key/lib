# tools/__init__.py
from .time_tools import get_current_time
# from .weather_tools import get_weather  <-- future tools

# Group them into a list for easy agent consumption
time_assistant_tools = [get_current_time]
