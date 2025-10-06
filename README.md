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
