import yfinance as yf

def getPercentageChange(ticker):
    ticker = yf.Ticker(ticker)
    stockInfo = ticker.fast_info

    previousClose = stockInfo.get("previousClose")
    price = stockInfo.get("lastPrice")

    if not previousClose or not price:
        return None, None, None
    
    percentChange = (price - previousClose) / previousClose

    return percentChange, previousClose, price