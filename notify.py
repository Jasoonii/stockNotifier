import requests

def sendAlert(notifyTopic, ticker, percentChange, currentPrice):
    message = f"{ticker} is down {abs(percentChange) * 100:.1f}% today (${currentPrice:.2f})"

    requests.post(
        f"https://ntfy.sh/{notifyTopic}",
        data=message,
        headers={"Title": f"STOCK DROP: {ticker}"}
    )
    print(f"[ALERT SENT] {message}")