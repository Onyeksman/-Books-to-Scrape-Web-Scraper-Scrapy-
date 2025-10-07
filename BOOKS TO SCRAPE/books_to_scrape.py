import scrapy
from scrapy.crawler import CrawlerProcess


class BooksSpider(scrapy.Spider):
    # Spider name (used when running Scrapy projects)
    name = "books"

    # Starting URL for the spider
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    # Custom Scrapy settings for this spider
    custom_settings = {
        "FEEDS": {
            "books_info.csv": {       # Output file name
                "format": "csv",       # Save data in CSV format
                "overwrite": True,     # Replace old file if it exists
                "encoding": "utf-8-sig",  # Ensure proper character encoding
            },
        },
        "LOG_LEVEL": "INFO",           # Reduce log noise (show only important info)
    }

    def parse(self, response):
        """
        Main parsing method.
        Called automatically by Scrapy for each response (page) received.
        Extracts book information and handles pagination.
        """

        # Select all book containers on the current page
        books = response.css("article.product_pod")
        self.logger.info(f"📖 Found {len(books)} books on {response.url}")

        # Loop through each book element and extract data
        for book in books:
            # Extract book title
            title = book.css("h3 a::attr(title)").get(default="").strip()

            # Extract price and clean unwanted characters
            price = book.css("p.price_color::text").get(default="").replace("Â", "").strip()

            # Extract availability text (clean spaces and newlines)
            availability = book.css("p.instock.availability::text").getall()
            availability = "".join([a.strip() for a in availability if a.strip()])

            # Extract star rating (class name format: "star-rating Three")
            rating = book.css("p.star-rating::attr(class)").get(default="").replace("star-rating", "").strip()

            # Extract full image URL (join relative path with domain)
            image_url = response.urljoin(book.css("div.image_container a img::attr(src)").get(default=""))

            # Yield a dictionary containing extracted book data
            yield {
                "Book Title": title,
                "Book Price": price,
                "Instock Availability": availability,
                "Rating": rating,
                "Image URL": image_url,
            }

        # ---- Pagination Handling ----
        # Check if there’s a “Next” button linking to another page
        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            # Follow the next page link and call `parse()` again
            yield response.follow(next_page, callback=self.parse)


# Run the spider directly (outside Scrapy project)
if __name__ == "__main__":
    # Initialize Scrapy's crawler process
    process = CrawlerProcess()

    # Register the spider class
    process.crawl(BooksSpider)

    # Start the crawling process
    process.start()
