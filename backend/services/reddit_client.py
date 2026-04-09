import praw
from fastapi import HTTPException
from backend.config import settings

class RedditClient:
    def __init__(self):
        self.client_id = settings.reddit_client_id
        self.client_secret = settings.reddit_client_secret
        self.redirect_uri = settings.reddit_redirect_uri
        self.user_agent = "web:RedditHiveMind:v1.0.0 (by /u/your_username)"

    def get_auth_url(self, state: str) -> str:
        reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            user_agent=self.user_agent,
        )
        return reddit.auth.url(scopes=["identity", "history"], state=state, duration="permanent")

    def authorize(self, code: str) -> str:
        reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            user_agent=self.user_agent,
        )
        try:
            refresh_token = reddit.auth.authorize(code)
            return refresh_token
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to authorize: {str(e)}")

    def get_user_client(self, refresh_token: str) -> praw.Reddit:
        return praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=refresh_token,
            user_agent=self.user_agent,
        )

reddit_client = RedditClient()
