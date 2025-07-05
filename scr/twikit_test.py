import asyncio
import os
from twikit import Client

async def main():
    client = Client()
    username = os.getenv('TWITTER_USERNAME')
    email = os.getenv('TWITTER_EMAIL') 
    password = os.getenv('TWITTER_PASSWORD')
    if not password:
        raise ValueError("TWITTER_PASSWORD environment variable is not set.")
    if username:
        await client.login(auth_info_1=username, password=password)
    elif email:
        await client.login(auth_info_1=email, password=password)
    else:
        raise ValueError("Neither TWITTER_USERNAME nor TWITTER_EMAIL environment variables are set.")
    tweets = await client.search_tweet('Python programming', 'Latest')

    for tweet in tweets:
        print(f"{tweet.user.name}: {tweet.text}")

asyncio.run(main())