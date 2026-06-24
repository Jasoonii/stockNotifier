from stocks import stockList, alertThreshold
from check import getPercentageChange
from notify import sendAlert
from scraper import getNewsArticles
from agent import getStockVerdict
import os

def run():
    print("Starting script")

    ntfyTopic = os.getenv("NTFY_TOPIC")

    for ticker in stockList:
        percentChange, previousClose, lastPrice = getPercentageChange(ticker)

        if percentChange is None:
            print(f"[WARNING] Could not find information on {ticker}")
            continue

        print(f"{ticker}: {percentChange * 100:.2f}% from previousClose")

        if percentChange <= alertThreshold:
            print(f"{ticker} is {percentChange * 100:.2f}% from previous close. Evaluating drop.")

            articles = getNewsArticles(ticker)

            if articles:
                print(f"Claude beginning evaluations for {ticker}.")

                verdict = getStockVerdict(ticker, articles)
            else:
                print(f"Couldn't get articles for {ticker}")
                verdict = None

            sendAlert(ntfyTopic, ticker, percentChange, lastPrice, verdict)

    print("Done")

if __name__ == "__main__":
    run()
