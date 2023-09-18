import scrapy


class CastoramaSpider(scrapy.Spider):
    name = 'cast_spider'
    start_urls = ['https://www.castorama.ru/']

    def parse(self, response, **kwargs):
        link = 'https://www.castorama.ru/decoration/interior-items-souvenirs/'
        yield response.follow(link, callback=self.parse_castorama)

    def parse_castorama(self, response):
        yield {
            'product_name': list(map(str.strip, (response.xpath(
                "//a[@class='product-card__name ga-product-card-name']/text()").getall()))),
            'product_photo': list(map(str.strip, (response.xpath(
                "//img[@class='product-card__img js-lazy-image lazy-image']/@src").getall()))),
            'product_link': list(map(str.strip, (response.xpath(
                "//a[@class='product-card__name ga-product-card-name']/@href").getall()))),
            'product_price': list(map(str.strip, (response.xpath(
                "//span[@class='price']/span/span/text()").getall())))
        }
