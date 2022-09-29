import requests

from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

from .logger import Logger

logger = Logger()

# Function That Converts Numbers To Human Format (e.i, 1.000 to 1k)
def human_format(num : Optional[Any]):
	num = float('{:.3g}'.format(num))
	magnitude = 0
	while abs(num) >= 1000:
		magnitude += 1
		num /= 1000.0

	return "{}{}".format("{:f}".format(num).rstrip("0").rstrip("."), ["", "k", "M", "B", "T"][magnitude])

# Function That Returns The Difference Between Two Dicts
def get_difference(dict1 : dict, dict2 : dict) -> dict:
	return {key: dict1[key] for key in dict1 if dict1[key] != dict2[key]}

# Function That Returns The Difference Between Two Lists
def get_difference_list(list1 : list, list2 : list) -> list:
	return [x for x in list1 if x not in list2]

# Function That Chunks A String If It's Longer Than The Specified Length
def chunk(string : str, length : int) -> list:
	return [string[i:i+length] for i in range(0, len(string), length)]

# Function that returns base64 of data parameter with padding characters to ensure its length is a multiple of 4.
def pad_base64(data : str) -> str:	
	return data + "=" * (-len(data) % 4)

def trim(text: str, limit: int) -> str:
	return text[: limit - 3].strip() + "..." if len(text) > limit else text