# Web Crawler for Student Document URLs

A **Python-based web crawler** using **Selenium** and **BeautifulSoup** to perform a **depth-first crawl** of a website, extract URLs, and identify pages containing document view links. Ideal for scraping educational websites for resources such as past papers, documents, and other student materials.

---

## Features

- Depth-first web crawling starting from a base URL
- Tracks URL depth and keeps statistics on processed pages
- Detects "ending links" that do not lead to other pages
- Extracts document-related URLs based on link text, IDs, and patterns
- Filters out irrelevant URLs (images, admin pages, media files)
- Handles dynamic content with Selenium
- Randomized delays to mimic human browsing
- Exports results to CSV files:
  - `pastpapers_urls.csv` (all URLs with depth and ending link info)
  - `document_urls.csv` (document view URLs only)

---

## Tech Stack

- Python 3.x
- Selenium
- BeautifulSoup (bs4)
- Chrome WebDriver
- CSV, URL parsing, and standard Python libraries

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/student-web-crawler.git
cd student-web-crawler

# 2. Install dependencies
pip install selenium beautifulsoup4

# 3. Download ChromeDriver compatible with your Chrome version
#    and ensure it's in your PATH (manual step)

# 4. Run the crawler
python crawler.py

