import yfinance as yf

def getPercentageChange(ticker):
    ticker = yf.Ticker(ticker)
    stockInfo = ticker.info

    previousClose = stockInfo.get("regularMarketPreviousClose")
    price = stockInfo.get("currentPrice")

    if not previousClose or not price:
        return None, None, None
    
    percentChange = (price - previousClose) / previousClose

    return percentChange, previousClose, price