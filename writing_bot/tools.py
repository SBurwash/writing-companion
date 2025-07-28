import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool

# Setup module logger
logger = logging.getLogger(__name__)


@tool
def check_weather(location: str) -> str:
    '''Return the weather forecast for the specified location.'''
    return f"It's always sunny in {location}"