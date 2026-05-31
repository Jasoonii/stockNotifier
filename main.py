from stocks import stockList, ntfyTopic, alertThreshold
from check import getPercentageChange
from notify import sendAlert

def run():
    print("Starting script")

    for ticker in stockList:
        percentChange, openPrice, lastPrice = getPercentageChange(ticker)

        if percentChange is None:
            print(f"[WARNING] Could not find information on {ticker}")
            continue

        print(f"{ticker}: {percentChange * 100:.2f}% from open")

        if percentChange <= alertThreshold:
            sendAlert(ntfyTopic, ticker, percentChange, lastPrice)

    print("Done")

if __name__ == "__main__":
    run()
