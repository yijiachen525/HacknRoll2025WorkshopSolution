import json

import scrapy
from typing import Any, Dict, Iterable
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
from scrapy import Field, Item

from settings import USER_AGENT, KAFKA_TOPIC_MYSTERY_PICTURE


class MysteryPictureAPIItem(Item):
    api_response = Field()


class MysteryPictureSpider(scrapy.Spider):
    name = "mystery-picture-spider"
    custom_settings = {"KAFKA_TOPIC": KAFKA_TOPIC_MYSTERY_PICTURE}
    batch_size = 50

    def start_requests(self) -> Iterable[Request]:
        # start with row = 0
        yield Request(
            url="http://localhost:9999/rows/0",
            headers={"User-Agent": USER_AGENT},
            meta={"row": 0},
        )

    def parse(self, response: Response, **kwargs: Any) -> Any:
        yield MysteryPictureAPIItem(api_response=response.text)

        # get the next row data
        next_row = response.meta["row"] + 1

        # If still has more rows to scrape
        if next_row <= 499:
            yield Request(
                url=f"http://localhost:9999/rows/{next_row}",
                headers={"User-Agent": USER_AGENT},
                meta={"row": next_row},
            )
