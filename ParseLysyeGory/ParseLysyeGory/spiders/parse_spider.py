from ParseLysyeGory.items import ParselysyegoryItem
from urllib.parse import urljoin

import scrapy

class ParseLysyeGorySpider(scrapy.Spider):
    name = "ParseLysyeGory"
    start_urls = [
        'http://adm.lysyegory.ru/base/novosti?page=1',
    ]
    visited_urls = []
 
    def parse(self, response):
        if response.url not in self.visited_urls:
            self.visited_urls.append(response.url)
            for post_link in response.xpath('//h2[@class="value"]/a/@href').extract():
                url = urljoin(response.url, post_link)
                yield response.follow(url, callback=self.parse_post)
                
            next_page_selector = '.pagebar_page + a::attr(href)'
            next_page = response.css(next_page_selector).extract_first()
            if next_page:
                yield scrapy.Request(
                response.urljoin(next_page),
                callback = self.parse)
            
    def parse_post(self, response):
        item = ParselysyegoryItem()
        body = response.xpath('//div[@class="value"]/p/span/text()').extract()
        if not body:
            body = response.xpath('//div[@class="value"]/p/text()').extract()
        if not body:
            body = response.xpath('//div[@class="value"]/span/text()').extract()
        if not body:
            body = response.xpath('//div[@class="value"]/p/span/span/span/text()').extract()
        if not body:
            body = response.xpath('//div[@class="value"]/p/span/strong/span/text()').extract()
        if not body:
            body = response.xpath('//div[@class="value"]/p/span/span/text()').extract()
        if not body:
            body = response.xpath('//div[@class="value"]/p/span/strong/text()').extract()
        item['body'] = body
        item['url'] = response.url
        date = response.xpath('//div[@class="bar_item bi_date_pub"]/time/text()').extract()
        if not date:
            date = response.xpath('//div[@class="info_bar"]/div/time/text()').extract()
        item['date'] = date
        yield item