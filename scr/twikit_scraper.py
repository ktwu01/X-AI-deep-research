import os
import pandas as pd
import asyncio
from twikit import Client
from datetime import datetime
import time

# Import your existing config
from twitter_query import MIN_RETWEETS, MIN_LIKES

class TwitterScraperTwikit:
    def __init__(self):
        self.client = Client('en-US')
        self.logged_in = False
    
    async def login(self):
        """Login using credentials (no API key needed)"""
        
        # You'll need to set these environment variables
        username = os.getenv('TWITTER_USERNAME')
        email = os.getenv('TWITTER_EMAIL') 
        password = os.getenv('TWITTER_PASSWORD')
        
        if not all([username, email, password]):
            print("Set TWITTER_USERNAME, TWITTER_EMAIL, TWITTER_PASSWORD environment variables")
            print("Note: Use a throwaway account, not your main account")
            return False

        # At this point, username, email, and password are guaranteed to be str, not None
        try:
            print("Logging into Twitter...")
            await self.client.login(
                auth_info_1=str(username),
                auth_info_2=str(email),
                password=str(password)
            )
            
            print("✓ Successfully logged in")
            self.logged_in = True
            return True
            
        except Exception as e:
            print(f"Login failed: {e}")
            print("Tips:")
            print("- Use email/username that works in browser")
            print("- Check if account needs verification")
            print("- Try with VPN if IP is blocked")
            return False
    
    async def search_tweets(self, query, count=50):
        """Search tweets with engagement filtering"""
        
        if not self.logged_in:
            if not await self.login():
                return []
        
        try:
            print(f"Searching for: {query}")
            print(f"Target count: {count}")
            
            # Search tweets
            tweets = await self.client.search_tweet(
                query=query,
                product='Latest',  # or 'Top' for top tweets
                count=count
            )
            
            print(f"Raw search returned {len(tweets)} tweets")
            
            # Process and filter tweets
            filtered_tweets = []
            
            for tweet in tweets:
                try:
                    # Extract metrics
                    retweets = tweet.retweet_count or 0
                    likes = tweet.favorite_count or 0
                    replies = tweet.reply_count or 0
                    quotes = tweet.quote_count or 0
                    
                    # Apply engagement filter
                    if retweets >= MIN_RETWEETS or likes >= MIN_LIKES:
                        filtered_tweets.append({
                            'id': tweet.id,
                            'text': tweet.text.replace('\n', ' '),
                            'author': tweet.user.screen_name,
                            'author_name': tweet.user.name,
                            'created_at': tweet.created_at,
                            'retweets': retweets,
                            'likes': likes,
                            'replies': replies,
                            'quotes': quotes,
                            'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
                        })
                        
                except Exception as e:
                    print(f"Error processing tweet: {e}")
                    continue
            
            print(f"Found {len(filtered_tweets)} tweets meeting engagement criteria")
            print(f"Filter: RT≥{MIN_RETWEETS} OR Likes≥{MIN_LIKES}")
            
            return filtered_tweets
            
        except Exception as e:
            print(f"Search failed: {e}")
            return []
    
    async def search_multiple_queries(self, queries, count_per_query=25):
        """Search multiple queries and combine results"""
        
        all_tweets = []
        
        for i, query in enumerate(queries):
            print(f"\n--- Query {i+1}/{len(queries)} ---")
            tweets = await self.search_tweets(query, count_per_query)
            all_tweets.extend(tweets)
            
            # Rate limiting between queries
            if i < len(queries) - 1:
                print("Waiting 3 seconds between queries...")
                await asyncio.sleep(3)
        
        return all_tweets

async def main():
    """Main scraping function"""
    
    scraper = TwitterScraperTwikit()
    
    # Define search queries (simplified for twikit)
    queries = [
        'AI research release',
        'LLM launch',
        'AI model announced',
        'machine learning breakthrough',
        'OpenAI released',
        'AI paper published'
    ]
    
    print("=== Twitter Scraper with Twikit ===")
    print(f"Queries: {queries}")
    print(f"Engagement filter: RT≥{MIN_RETWEETS} OR Likes≥{MIN_LIKES}")
    
    # Search tweets
    all_tweets = await scraper.search_multiple_queries(queries, count_per_query=20)
    
    if not all_tweets:
        print("No tweets found or login failed")
        return
    
    # Create DataFrame and remove duplicates
    df = pd.DataFrame(all_tweets)
    df = df.drop_duplicates(subset=['id'], keep='first')
    df = df.sort_values(['retweets', 'likes'], ascending=False)
    
    print(f"\nTotal unique high-engagement tweets: {len(df)}")
    
    # Save results
    os.makedirs('data', exist_ok=True)
    output_file = 'data/twikit_ai_research_tweets.csv'
    df.to_csv(output_file, index=False)
    
    print(f"Saved to {output_file}")
    
    # Display top results
    print(f"\nTop tweets by engagement:")
    for idx, row in df.head(10).iterrows():
        print(f"\n- @{row['author']} | RT:{row['retweets']} L:{row['likes']}")
        print(f"  {row['text'][:100]}...")
        print(f"  {row['url']}")

def setup_credentials():
    """Helper to set up Twitter credentials"""
    
    print("=== Twikit Setup Instructions ===")
    print("1. Install: pip install twikit")
    print("2. Set environment variables:")
    print("   export TWITTER_USERNAME='your_username'")
    print("   export TWITTER_EMAIL='your_email@example.com'") 
    print("   export TWITTER_PASSWORD='your_password'")
    print("")
    print("IMPORTANT:")
    print("- Use a throwaway Twitter account, not your main one")
    print("- Account should be verified and have normal activity")
    print("- twikit simulates browser login, so normal account restrictions apply")
    print("")
    print("Run: python twikit_scraper.py")

if __name__ == "__main__":
    # Check if credentials are set
    if not all([os.getenv('TWITTER_USERNAME'), os.getenv('TWITTER_EMAIL'), os.getenv('TWITTER_PASSWORD')]):
        setup_credentials()
    else:
        # Run the scraper
        asyncio.run(main())