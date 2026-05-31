import yfinance as yf

def getPercentageChange(ticker):
    ticker = yf.Ticker(ticker)
    stockInfo = ticker.fast_info

    openPrice = stockInfo.get("open")
    price = stockInfo.get("lastPrice")

    if not openPrice or not price:
        return None, None, None
    
    percentChange = (price - openPrice) / openPrice

    return percentChange, openPrice, price