import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.reddit.com/user/furballThatSpeaks/")
        await page.wait_for_selector("shreddit-profile-comment", timeout=10000)
        
        comments = await page.locator("shreddit-profile-comment").all()
        if comments:
            html = await comments[0].inner_html()
            print("HTML Snippet:\n", html[:1500])
        else:
            print("No comments found.")
        await browser.close()

asyncio.run(main())
