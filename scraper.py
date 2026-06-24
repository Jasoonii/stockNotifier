import requests
from bs4 import BeautifulSoup
import yfinance as yf

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def getNewsArticles(ticker, maxArticles=7):
    stock = yf.Ticker(ticker)
    newsItems = stock.news

    if not newsItems:
        return []

    articles = []

    for item in newsItems[:maxArticles]:
        title = item.get("content", {}).get("title", "No Title")
        url = (
            item.get("content", {}).get("canonicalUrl", {}).get("url")
            or item.get("content", {}).get("clickThroughUrl", {}).get("url")
        )

        if not url:
            continue

        content = scrapeArticle(url)

        if content:
            articles.append({
                "title": title,
                "url": url,
                "content": content
            })

    return articles


def scrapeArticle(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove html tags
        for tag in soup(["script", "style", "nav", "footer", "aside", "header", "form"]):
            tag.decompose()

        # Try article body first, fall back to all paragraphs
        article = soup.find("article")
        if article:
            paragraphs = article.find_all("p")
        else:
            paragraphs = soup.find_all("p")

        text = " ".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40)

        return text if len(text) > 200 else None

    except Exception as e:
        print(f"[SCRAPER] Failed to scrape {url}: {e}")
        return None