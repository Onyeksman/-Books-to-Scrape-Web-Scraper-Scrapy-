import scrapy
from scrapy.crawler import CrawlerProcess


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    custom_settings = {
        "FEEDS": {
            "books_info.csv": {
                "format": "csv",
                "overwrite": True,
                "encoding": "utf-8-sig",
            },
        },
        "LOG_LEVEL": "INFO",
    }

    def parse(self, response):
        books = response.css("article.product_pod")
        self.logger.info(f"📖 Found {len(books)} books on {response.url}")

        for book in books:
            title = book.css("h3 a::attr(title)").get(default="").strip()
            price = book.css("p.price_color::text").get(default="").replace("Â", "").strip()
            availability = book.css("p.instock.availability::text").getall()
            availability = "".join([a.strip() for a in availability if a.strip()])
            rating = book.css("p.star-rating::attr(class)").get(default="").replace("star-rating", "").strip()
            image_url = response.urljoin(book.css("div.image_container a img::attr(src)").get(default=""))

            yield {
                "Book Title": title,
                "Book Price": price,
                "Instock Availability": availability,
                "Rating": rating,
                "Image URL": image_url,
            }

        # pagination
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(BooksSpider)
    process.start()
