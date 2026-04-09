import re
import urllib.parse
from playwright.async_api import async_playwright

async def scrape_reddit_posts(query: str, limit: int = 15) -> list[dict]:
    """Uses Playwright headless browser to load Reddit Search and extract live posts."""
    results = []
    
    async with async_playwright() as p:
        # Launch headless browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        url = f"https://www.reddit.com/search/?q={urllib.parse.quote(query)}&type=link"
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=15000)
            
            # Reddit loads search results dynamically into 'shreddit-post' elements
            # Wait a moment for them to be visible
            await page.wait_for_selector('shreddit-post', timeout=10000)
            
            posts = await page.locator('shreddit-post').all()
            
            for post in posts[:limit]:
                try:
                    title = await post.get_attribute("post-title") or ""
                    subreddit = await post.get_attribute("subreddit-prefixed-name") or "r/all"
                    
                    # Fetch text content inside the post
                    # It might be in a slot='text-body' or directly as plain text
                    # We can evaluating text content via JS more reliably for Shadow DOMs
                    body = await post.evaluate("el => { const body = el.querySelector('[slot=\"text-body\"]'); return body ? body.textContent : ''; }")
                    if not body:
                        # Fallback if no text-body exists
                        body = ""
                        
                    # Clean up body
                    body = re.sub(r'\s+', ' ', body).strip()
                    
                    if not body and not title:
                        continue
                        
                    # If body is empty, fall back to analyzing the title as the organic sentiment
                    sentiment_text = body if len(body) > len(title) else title
                        
                    score_attr = await post.get_attribute("score")
                    try:
                        score = int(score_attr) if score_attr else 0
                    except (ValueError, TypeError):
                        score = 0
                        
                    post_id = await post.get_attribute("id") or f"organic_{len(results)}"
                    
                    results.append({
                        "comment_id": post_id,
                        "subreddit": subreddit.replace("r/", ""),
                        "thread_id": post_id,
                        "thread_title": title,
                        "body": sentiment_text,
                        "score": score
                    })
                    
                except Exception as e:
                    print(f"Scrape parse error for item: {e}")
                    continue
                    
        except Exception as e:
            print(f"Scrape navigation/timeout error: {e}")
        finally:
            await browser.close()
            
    return results
