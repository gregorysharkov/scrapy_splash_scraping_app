from pathlib import Path

import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest

from ..items import EpisodeItem

    output_path = Path() / "data" / "episodes"

class EpisodeScraper(scrapy.Spider):
    name = "episode"
    allowed_domains = ["toresaid.com"]
    start_urls = [
        "https://toresaid.com/episodeList.cshtml",
    ]

    def start_requests(self):
        url = self.start_urls[0]
        self.log(f"Going for page {url}")
        request = SplashRequest(
            url=url,
            callback=self.parse,
            args={"wait": 2},
        )
        yield request

    def parse(self, response):
        """get list of episodes to be parsed and parse each one"""
        episode_list = response.xpath("//div[contains(@class, 'u-list-item')]")[:3]

        for idx, episode_container in enumerate(episode_list):
            episode = self.parse_episode(episode_container, idx)
            yield episode

    def parse_episode(self, episode_container, idx: int):
        """parse single item in the article list"""

        episode_selector = episode_container.xpath(
            "//div[contains(@class, 'u-list-item')]"
        )[idx]
        itl = ItemLoader(
            EpisodeItem(), response=episode_container, selector=episode_selector
        )
        self.log(f"{episode_container=}")
        itl.add_xpath("title", ".//h4")
        itl.add_xpath("summary", ".//p/text()")
        itl.add_xpath(
            "url", "//a[contains(@href, 'api/episode/printtranscript')]/@href",
        )

        episode = itl.load_item()
        return episode

    # def download_episode(self, response, title: str):
    #     '''download the file from from the response'''