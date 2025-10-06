# 🕷️ Books to Scrape – Web Scraper (Scrapy)

A robust, fully automated **web scraping project** built with **Scrapy** to extract book data from the website [Books to Scrape](https://books.toscrape.com).  

This spider crawls all book listings, page by page, and exports a clean dataset (`books_info.csv`) containing titles, prices, ratings, availability, and cover image URLs — ready for data analysis or visualization in the accompanying **Streamlit Books Dashboard**.

---

## 🧠 Project Overview

This project demonstrates **end-to-end web data extraction** using Python’s `Scrapy` framework.  
It automatically crawls every page of the “Books to Scrape” catalog, normalizes the data, and outputs a structured CSV file suitable for analytics, reporting, or dashboards.

**Key Goals:**
- Automate data collection from a paginated e-commerce-like site.
- Export structured book data into a clean, ready-to-use format.
- Form the backend data source for an interactive Streamlit dashboard.

---

## 📦 Features

| Feature | Description |
|----------|-------------|
| 🕷️ **Automated Crawling** | Crawls every page of the Books to Scrape catalog. |
| 📘 **Data Extraction** | Extracts book title, price, rating, stock availability, and image URL. |
| 🔁 **Pagination Handling** | Automatically follows “Next” page links until all books are scraped. |
| 💾 **Clean CSV Export** | Outputs data to `books_info.csv` with UTF-8 encoding for Excel/Streamlit compatibility. |
| 🧩 **Plug-and-Play** | The resulting CSV works directly with the [Books Dashboard (Streamlit)](../streamlit_books_dashboard.py). |
| 🧱 **Lightweight & Portable** | Single-file script — no project scaffolding needed. |

---

## ⚙️ How It Works

### 1️⃣ Spider Definition
```python
class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]
```
The spider starts from the first catalog page and parses all book cards (article.product_pod).

---

### 2️⃣ Data Extraction

For each book, the spider collects:


| Field            | Selector                       | Description                                        |
| ---------------- | ------------------------------ | -------------------------------------------------- |
| **Book Title**   | `h3 a::attr(title)`            | The title of the book                              |
| **Book Price**   | `p.price_color::text`          | Price including the currency symbol                |
| **Availability** | `p.instock.availability::text` | In-stock or out-of-stock info                      |
| **Rating**       | `p.star-rating::attr(class)`   | Extracted as a textual rating (“One”, “Two”, etc.) |
| **Image URL**    | `img::attr(src)`               | Full image URL (auto-joined with site base)        |

Each book is yielded as a structured Python dictionary, which Scrapy automatically converts to CSV.

---

### 3️⃣ Pagination

next_page = response.css("li.next a::attr(href)").get()
if next_page:
    yield response.follow(next_page, callback=self.parse)

The spider detects the “Next” button on each page and recursively crawls until no further pages exist (all 1000 books).

---

### 4️⃣ Output Configuration

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

* The spider saves all results into books_info.csv.
* UTF-8 encoding ensures compatibility with Excel, Streamlit, and Power BI.
* Clean logs (INFO level) make it suitable for client or production environments.


5️⃣ Standalone Execution

This spider can run without the Scrapy CLI using:

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(BooksSpider)
    process.start()

So you can launch it simply with:

python books_spider.py

📊 Sample Output

After completion, you’ll find a file books_info.csv like this:

| Book Title           | Book Price | Instock Availability    | Rating | Image URL                                                     |
| -------------------- | ---------- | ----------------------- | ------ | ------------------------------------------------------------- |
| A Light in the Attic | £51.77     | In stock (22 available) | Three  | [https://books.toscrape.com/](https://books.toscrape.com/)... |
| Tipping the Velvet   | £53.74     | In stock (20 available) | One    | [https://books.toscrape.com/](https://books.toscrape.com/)... |


This file can be used directly in your Streamlit dashboard or any data visualization tool.

🧰 Tech Stack

| Purpose                      | Tool                                           |
| ---------------------------- | ---------------------------------------------- |
| **Web Scraping**             | [Scrapy](https://scrapy.org)                   |
| **Language**                 | Python 3.8+                                    |
| **Data Format**              | CSV (UTF-8)                                    |
| **Visualization (optional)** | Streamlit + Plotly (for dashboard integration) |


⚙️ Installation & Usage
1️⃣ Clone this repository

git clone https://github.com/<your-username>/books-to-scrape-scraper.git
cd books-to-scrape-scraper

2️⃣ Install dependencies

pip install scrapy

3️⃣ Run the spider

python books_spider.py

4️⃣ View output

A file named books_info.csv will appear in the same directory.

🧠 Integration with Streamlit Dashboard

This scraper is part of a two-step data project:

1.    Data Extraction: (This script) Scrape and save books_info.csv.

2.    Data Visualization: Use the companion app streamlit_books_dashboard.py to interactively explore the dataset.

You can find the Streamlit dashboard version here 👉 Books Dashboard Repo
 (replace with your actual link).

🧾 License

This project is released under the MIT License.
You’re free to use, modify, or build upon it with proper credit.

👨‍💻 Author

Onyekachi Ejimofor
Python Developer | Web Scraping & Automation | Data Visualization
📧 Email: onyeife@gmail.com
🌐 GitHub: https://github.com/Onyeksman
💼 LinkedIn: www.linkedin.com/in/onyekachiejimofor
