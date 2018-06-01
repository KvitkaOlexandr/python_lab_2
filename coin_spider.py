import scrapy
from scrapy import Selector


class CoinSpider(scrapy.Spider):
    name = "coins"
    #base_url = 'https://forum.finance.ua/viewforum.php?f=31'
    base_url = 'http://www.actuarialoutpost.com/actuarial_discussion_forum/forumdisplay.php?' \
               's=a79c5445e458992b68b570bc8cfc2775&f=80&order=desc&page='

    def start_requests(self):
        for i in range(10):
            yield scrapy.Request(self.base_url + str(i))


    def parse(self, response):
        topics = Selector(response).xpath("//a[contains(@id, 'thread_title_')]")
        for topic in topics:
            url = response.urljoin(topic.xpath(".//@href").extract_first())
            request = scrapy.Request(url, callback=self.parse_thread_pages)
            request.meta['topic'] = topic.xpath('.//text()').extract_first()
            yield request

    def parse_thread_pages(self, response):
        sel = Selector(response) \
            .xpath("//div[contains(@class, 'pagenav')]/table/tr/td[contains(@nowrap, 'nowrap')]/a/@href")
        pages = sel.re_first(r'.*page=(\d+)')
        link = sel.re_first(r'(.*page=).*')
        if pages is None:
            yield from self.parse_thread_messages(response)
        else:
            for p in range(int(pages)):
                url = response.urljoin(link + str(p + 1))
                request = scrapy.Request(url, callback=self.parse_thread_messages)
                request.meta['topic'] = response.meta['topic']
                yield request

    def parse_thread_messages(self, response):
        topic = response.meta['topic']
        messages = Selector(response).xpath("//div[contains(@id, 'post_message_')]/text()").re(r"\r*\n*\s*(.+)")
        authors = response.css("a.bigusername::text").extract()
        dates = Selector(response) \
            .xpath("//table[contains(@id, 'post')]/tr/td[contains(@class, 'thead')]") \
            .re(r'.*(\d{2}-\d{2}-\d{4},\s\d{2}:\d{2}\s[A-Za-z]{2}).*')
        for item in zip(authors, messages, dates):
            if len(item[1].strip()) > 0:
                yield {
                    'topic': topic,
                    'author': item[0],
                    'message': item[1],
                    'date': item[2]
                }