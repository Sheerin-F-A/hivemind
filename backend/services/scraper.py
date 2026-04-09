import re
import urllib.parse
from playwright.async_api import async_playwright

# Discard entries containing these automation strings completely
BOT_FILTER_TERMS = ["i am a bot", "action was performed automatically", "opt-out", "beep boop", "automoderator", "bot account"]
# Log but flag as Spam explicitly for NLP algorithms bypassing
SPAM_FILTER_TERMS = ["crypto", "nft", "solana", "eth", "giveaway", "free money"]

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
                        
                    # Bot Extinction Layer
                    lowercase_combined = f"{body} {title} {subreddit}".lower()
                    if any(bot_term in lowercase_combined for bot_term in BOT_FILTER_TERMS):
                        continue
                        
                    # If body is empty, fall back to analyzing the title as the organic sentiment
                    sentiment_text = body if len(body) > len(title) else title
                        
                    score_attr = await post.get_attribute("score")
                    try:
                        score = int(score_attr) if score_attr else 0
                    except (ValueError, TypeError):
                        score = 0
                        
                    # Authentic Spam Flagging
                    is_spam_flag = any(spam_term in lowercase_combined for spam_term in SPAM_FILTER_TERMS)
                        
                    post_id = await post.get_attribute("id") or f"organic_{len(results)}"
                    
                    results.append({
                        "comment_id": post_id,
                        "subreddit": subreddit.replace("r/", ""),
                        "thread_id": post_id,
                        "thread_title": title,
                        "body": sentiment_text,
                        "score": score,
                        "is_spam": is_spam_flag
                    })
                    
                except Exception as e:
                    print(f"Scrape parse error for item: {e}")
                    continue
                    
        except Exception as e:
            print(f"Scrape navigation/timeout error: {e}")
        finally:
            await browser.close()
            
    return results

async def scrape_reddit_user(username: str, limit: int = 15) -> list[dict]:
    """Scrapes actual public comments dynamically from a user's organic profile."""
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        # Go straight to user's comments
        url = f"https://www.reddit.com/user/{username}/comments/"
        
        try:
            # We want to catch instances where the user doesn't exist (HTTP 404 or an element popup)
            res = await page.goto(url, wait_until="networkidle", timeout=15000)
            if res and res.status == 404:
                await browser.close()
                return []
                
            # Recent reddit interface hides comments inside 'shreddit-comment' or 'p' tags inside feed
            await page.wait_for_selector('shreddit-comment, p', timeout=8000)
            
            # Find all comments natively
            comments = await page.locator('shreddit-comment').all()
            
            # If shreddit-comment fails due to layout A/B testing, fallback grabbing raw text
            if not comments:
                raw_paragraphs = await page.locator('p').all()
                for p_node in raw_paragraphs[:limit]:
                    text = await p_node.inner_text()
                    text = text.strip()
                    if len(text) > 20:  # Skip raw UI short tags
                        results.append({
                            "body": text,
                            "subreddit": "unknown",
                            "score": 1
                        })
            else:
                for comment in comments[:limit]:
                    try:
                        divs = await comment.locator('div[slot="comment"]').all()
                        body = ""
                        for div in divs:
                            body += await div.inner_text() + " "
                        
                        body = re.sub(r'\s+', ' ', body).strip()
                        
                        if not body:
                            continue
                            
                        score_attr = await comment.get_attribute("score")
                        score = int(score_attr) if score_attr else 1
                        
                        # Try extracting native context for User profiles
                        subreddit = "unknown"
                        title = "Organic Personal Post"
                        try:
                            # A shreddit-comment usually implies it belongs to a post parent
                            href = await comment.evaluate("el => { const a = el.querySelector('a'); return a ? a.href : ''; }")
                            if href and "/r/" in href:
                                subreddit = href.split("/r/")[1].split("/")[0]
                                if "/comments/" in href:
                                    title = href.split("/comments/")[1].split("/")[1].replace("_", " ").title()
                        except Exception:
                            pass
                        
                        # Bot Extinction Layer for User
                        lowercase_combined = body.lower()
                        if any(bot_term in lowercase_combined for bot_term in BOT_FILTER_TERMS):
                            continue
                            
                        # Authentic Spam Flagging
                        is_spam_flag = any(spam_term in lowercase_combined for spam_term in SPAM_FILTER_TERMS)
                            
                        results.append({
                            "body": body,
                            "subreddit": subreddit,
                            "title": title,
                            "score": score,
                            "is_spam": is_spam_flag
                        })
                    except Exception:
                        continue
                        
        except Exception as e:
            print(f"User scrape error: {e}")
        finally:
            await browser.close()
            
    return results
