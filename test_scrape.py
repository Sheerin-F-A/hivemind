import asyncio
from backend.services.scraper import scrape_reddit_user

async def main():
    res = await scrape_reddit_user("furballThatSpeaks")
    print("Scraping finished.")
    for r in res[:5]:
        print(f"Data: {r}")

asyncio.run(main())
