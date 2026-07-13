import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

def getStockVerdict(ticker, articles):    
    articleText=""

    for index, article in enumerate(articles, 1):
        articleText += f"Article {index}: {article['title']} \n"
        articleText += article["content"][:2000]
        articleText += "\n\n"
    

    prompt = (
        f"The stock {ticker} dropped today over 3%."
        "Based on the following news articles, evaluate whether I should: BUY, SELL, or HOLD. the stock."
        "Explain your reasoning in 3-4 sentences, and explain if the drop is temporary or a fundamental."
        f"{articleText}"
    )


    response = client.messages.create(
        model = "claude-sonnet-4-6",
        max_tokens=300,
        system=(
            "You are a stock analyst. You evaluate news articles to decide if a stock drop is a buying opportunity, a sell, or neutral."
            "Start your responses with BUY, SELL, HOLD in all caps on its own line then explain your reasoning on a new line."
            "If earnings just came out any the company beat it heavily, it should be a buy, even if people are questioning spend on something like AI, an innovative technology which is the future"
            "If there is big controversy or scandal like faking earnings numbers, somebody important leaving the company, it could be a sell, or hold"
            "If people are mass selling, figure out why and determine if it's a buy, sell, or hold."
            "You are evaluating a buy, sell, or hold evaluation for a long term basis 1 year minimum"
        ),
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.content[0].text