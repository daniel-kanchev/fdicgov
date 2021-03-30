import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from fdicgov.items import Article
import requests
import json


class fdicgovSpider(scrapy.Spider):
    name = 'fdicgov'
    start_urls = ['https://www.fdic.gov/news/']

    def parse(self, response):
        jsonReq = json.loads(
            requests.get('https://www.fdic.gov/news/press-releases/2021/press-releases.json').text)
        articles = jsonReq['pressReleases']
        for article in articles:
            link = response.urljoin(article['href'])
            date = article["date"]
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//section//article//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()
        if not content:
            return

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
