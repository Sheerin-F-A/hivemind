import json
import random
import time

def generate_demo1():
    # Positive, Tech, AI, Futurology
    subs = ["Futurology", "artificial", "MachineLearning", "UpliftingNews", "technology", "programming"]
    comments = []
    
    current_time = int(time.time())
    
    for _ in range(120):
        sub = random.choice(subs)
        # Random time within the last 365 days
        past_time = current_time - random.randint(100, 31536000)
        
        # Positive sentiment bodies
        positive_bodies = [
            "This is absolutely incredibly fascinating! I love artificial intelligence.",
            "Great work on the neural network architecture! It really helps optimize the latency.",
            "Wow, this is a fantastic breakthrough for medical science. Very uplifting.",
            "I completely agree! The future looks incredibly bright and full of opportunities.",
            "Amazing tutorial. Thanks for sharing this detailed explanation.",
            "I'm super optimistic about where technology is heading next year.",
            "Brilliant analysis! You summarized the core issue perfectly.",
            "Excellent framework. We deployed it to production and it's running smoothly."
        ]
        
        is_spam = False
        body = random.choice(positive_bodies)
        
        comments.append({
            "subreddit": sub,
            "title": f"The future of {sub.lower()}",
            "body": body,
            "score": random.randint(5, 500),
            "is_spam": is_spam,
            "timestamp": past_time
        })
        
    with open('demo1.json', 'w') as f:
        json.dump(comments, f, indent=4)
        
def generate_demo2():
    # Negative, Crypto, Gaming
    subs = ["CryptoCurrency", "pcgaming", "mmo", "Bitcoin", "wallstreetbets", "gaming"]
    comments = []
    
    current_time = int(time.time())
    
    for _ in range(120):
        sub = random.choice(subs)
        past_time = current_time - random.randint(100, 31536000)
        
        negative_bodies = [
            "This is a terrible idea and will completely ruin the game economics.",
            "I hate how developers are releasing unfinished trash nowadays.",
            "Absolutely horrible investment. You are going to lose all your money.",
            "Worst update ever. It breaks completely basic functionality.",
            "This crypto token is a complete scam and total garbage.",
            "I'm extremely disappointed with the current state of the industry.",
            "Stop pushing this terrible narrative, it's completely wrong.",
            "This is incredibly frustrating and annoying to deal with."
        ]
        
        body = random.choice(negative_bodies)
        is_spam = True if "crypto" in body.lower() else False
        
        comments.append({
            "subreddit": sub,
            "title": f"Discussion about {sub.lower()}",
            "body": body,
            "score": random.randint(-50, 10),
            "is_spam": is_spam,
            "timestamp": past_time
        })
        
    with open('demo2.json', 'w') as f:
        json.dump(comments, f, indent=4)

if __name__ == "__main__":
    generate_demo1()
    generate_demo2()
    print("Generated demo1.json and demo2.json successfully.")
