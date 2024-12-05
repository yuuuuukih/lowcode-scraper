import os
from tqdm import tqdm
from typing import TypedDict, Literal

from .scraper import Scraper
from .utils.jsonl import jsonl
from .utils.myurl import myurl
from .utils.measure_exe_time import measure_exe_time



class BASE_DATA(TypedDict):
    """BASE_DATA型

    Notes:
        - id: データのユニークなID
        - url: スクレイピングしたいURL
    """
    id: str
    url: str