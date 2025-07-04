import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote
import time
import os

# Import your existing query config
from twitter_query import MIN_RETWEETS, MIN_LIKES

def convert_query_to_nitter(twitter_query):
    """Convert Twitter API query to Nitter search format"""
    # Remove Twitter API specific syntax
    query = twitter_query.replace('lang:en', '').replace('-is:retweet', '')
    
    # Simplify boolean operators for Nitter
    query = re.sub(r'\s+AND\s+', ' ', query)
    query = re.sub(r'\s+OR\s+', ' OR ', query)
    query = re.sub(r'[()]', '', query)
    
    # Clean up extra spaces
    query = ' '.join(query.split())
    
    return query.strip()

def parse_engagement_numbers(text):
    """Parse engagement numbers from Nitter (handles K, M notation)"""
    if not text:
        return 0
    
    # Remove commas and convert K/M notation
    text = text.strip().replace(',', '')
    
    if text.endswith('K'):
        return int(float(text[:-1]) * 1000)
    elif text.endswith('M'):
        return int(float(text[:-1]) * 1000000)
    elif text.isdigit():
        return int(text)
    else:
        return 0

def scrape_nitter_search(query, max_pages=3):
    """Scrape Nitter search results"""
    
    nitter_instances = [
        'https://nitter.net',
        'https://nitter.it',
        'https://nitter.pussthecat.org'
    ]
    
    encoded_query = quote(query)
    tweets = []
    
    for instance in nitter_instances:
        try:
            print(f"Trying {instance}...")
            
            for page in range(1, max_pages + 1):
                url = f"{instance}/search?q={encoded_query}&f=tweets"
                if page > 1:
                    url += f"&cursor={page}"
                
                print(f"Fetching page {page}: {url}")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"Failed to fetch page {page}: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                tweet_containers = soup.find_all('div', class_='timeline-item')
                
                if not tweet_containers:
                    print(f"No tweets found on page {page}")
                    break
                
                page_tweets = parse_tweets_from_html(tweet_containers)
                tweets.extend(page_tweets)
                
                print(f"Found {len(page_tweets)} tweets on page {page}")
                
                # Rate limiting
                time.sleep(2)
            
            if tweets:
                print(f"Successfully scraped {len(tweets)} tweets from {instance}")
                break
                
        except Exception as e:
            print(f"Error with {instance}: {e}")
            continue
    
    return tweets

def parse_tweets_from_html(tweet_containers):
    """Parse tweet data from HTML containers"""
    tweets = []
    
    for container in tweet_containers:
        try:
            # Extract tweet text
            tweet_content = container.find('div', class_='tweet-content')
            if not tweet_content:
                continue
            
            text = tweet_content.get_text(strip=True)
            
            # Extract engagement metrics
            stats = container.find('div', class_='tweet-stats')
            if not stats:
                continue
            
            # Parse retweets, likes, replies
            retweet_elem = stats.find('span', class_='tweet-stat')
            like_elem = stats.find_all('span', class_='tweet-stat')
            
            retweets = 0
            likes = 0
            replies = 0
            
            # Parse all stat elements
            for stat in stats.find_all('span', class_='tweet-stat'):
                stat_text = stat.get_text(strip=True)
                
                if 'retweet' in stat.get('title', '').lower():
                    retweets = parse_engagement_numbers(stat_text)
                elif 'like' in stat.get('title', '').lower() or 'favorite' in stat.get('title', '').lower():
                    likes = parse_engagement_numbers(stat_text)
                elif 'repl' in stat.get('title', '').lower():
                    replies = parse_engagement_numbers(stat_text)
            
            # Extract timestamp
            timestamp_elem = container.find('a', class_='tweet-date')
            timestamp = timestamp_elem.get('title', '') if timestamp_elem else ''
            
            # Extract username
            username_elem = container.find('a', class_='username')
            username = username_elem.get_text(strip=True) if username_elem else ''
            
            tweets.append({
                'text': text,
                'username': username,
                'timestamp': timestamp,
                'retweets': retweets,
                'likes': likes,
                'replies': replies
            })
            
        except Exception as e:
            print(f"Error parsing tweet: {e}")
            continue
    
    return tweets

def filter_high_engagement_tweets(tweets, min_retweets=MIN_RETWEETS, min_likes=MIN_LIKES):
    """Filter tweets by engagement thresholds"""
    
    filtered_tweets = []
    
    for tweet in tweets:
        if tweet['retweets'] >= min_retweets or tweet['likes'] >= min_likes:
            filtered_tweets.append(tweet)
    
    print(f"Filtered {len(tweets)} tweets to {len(filtered_tweets)} high-engagement tweets")
    print(f"Criteria: RT≥{min_retweets} OR Likes≥{min_likes}")
    
    return filtered_tweets

def main():
    """Main scraping function"""
    
    # Import your query
    from twitter_query import TWITTER_QUERY
    
    print("=== Nitter Tweet Scraper ===")
    print(f"Original query: {TWITTER_QUERY}")
    
    # Convert query for Nitter
    nitter_query = convert_query_to_nitter(TWITTER_QUERY)
    print(f"Nitter query: {nitter_query}")
    
    # Scrape tweets
    tweets = scrape_nitter_search(nitter_query, max_pages=2)
    
    if not tweets:
        print("No tweets found. Try a simpler query.")
        return
    
    # Filter by engagement
    high_engagement_tweets = filter_high_engagement_tweets(tweets)
    
    if high_engagement_tweets:
        # Save to CSV
        df = pd.DataFrame(high_engagement_tweets)
        df = df.sort_values(['retweets', 'likes'], ascending=False)
        
        output_file = 'data/nitter_high_engagement_tweets.csv'
        os.makedirs('data', exist_ok=True)
        df.to_csv(output_file, index=False)
        
        print(f"\nSaved {len(df)} high-engagement tweets to {output_file}")
        
        # Display top results
        print(f"\nTop tweets:")
        for idx, row in df.head(5).iterrows():
            print(f"- @{row['username']} | RT:{row['retweets']} L:{row['likes']}")
            print(f"  {row['text'][:100]}...")
            print()
    else:
        print("No tweets meet engagement criteria.")

if __name__ == "__main__":
    main()