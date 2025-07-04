import os
import requests
import pandas as pd
import ssl
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Disable SSL warnings for debugging
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SSLAdapter(HTTPAdapter):
    """Custom SSL adapter with relaxed SSL settings"""
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        # Allow legacy TLS versions if needed
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

def create_robust_session():
    """Create a requests session with retry logic and SSL configuration"""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    
    # Mount the custom SSL adapter
    adapter = SSLAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session

def fetch_tweets():
    """Fetch AI research tweets with robust error handling"""
    
    # Validate environment
    BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    if not BEARER_TOKEN:
        raise SystemExit('Set TWITTER_BEARER_TOKEN environment variable')
    
    # Import query configuration
    from twitter_query import TWITTER_QUERY, QUERY_PARAMS, MIN_RETWEETS, MIN_LIKES
    
    # Configuration
    HEADERS = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    
    PARAMS = {
        'query': TWITTER_QUERY,
        **QUERY_PARAMS
    }
    
    url = 'https://api.twitter.com/2/tweets/search/recent'
    
    # Create robust session
    session = create_robust_session()
    
    try:
        print("Attempting to connect to Twitter API...")
        resp = session.get(url, headers=HEADERS, params=PARAMS, timeout=30)
        resp.raise_for_status()
        
        print(f"Response status: {resp.status_code}")
        js = resp.json()
        
        # Process tweets with engagement filtering
        rows = []
        for tw in js.get('data', []):
            metrics = tw.get('public_metrics', {})
            retweets = metrics.get('retweet_count', 0)
            likes = metrics.get('like_count', 0)
            
            # Filter by engagement thresholds
            if retweets >= MIN_RETWEETS or likes >= MIN_LIKES:
                rows.append({
                    'id': tw.get('id'),
                    'created_at': tw.get('created_at'),
                    'author_id': tw.get('author_id'),
                    'text': tw.get('text', '').replace('\n', ' '),
                    'retweets': retweets,
                    'likes': likes,
                    'replies': metrics.get('reply_count', 0),
                    'quotes': metrics.get('quote_count', 0)
                })
        
        print(f"Found {len(js.get('data', []))} tweets, {len(rows)} meet engagement criteria (RT≥{MIN_RETWEETS} OR Likes≥{MIN_LIKES})")
        
        # Save results
        df = pd.DataFrame(rows)
        if not df.empty:
            df.sort_values(['retweets', 'likes'], ascending=False, inplace=True)
            
            # Ensure data directory exists
            os.makedirs('data', exist_ok=True)
            
            df.to_csv('data/trending_ai_research_tweets.csv', index=False)
            print(f'Saved {len(df)} tweets to data/trending_ai_research_tweets.csv')
            
            # Display top tweets
            print(f"\nHigh-engagement tweets (RT≥{MIN_RETWEETS} OR Likes≥{MIN_LIKES}):")
            for idx, row in df.head(5).iterrows():
                print(f"- RT:{row['retweets']} L:{row['likes']} | {row['text'][:80]}...")
        else:
            print('No tweets found.')
            
    except requests.exceptions.SSLError as e:
        print(f"SSL Error: {e}")
        print("Try running with alternative SSL configuration...")
        return fetch_tweets_alternative()
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return None

def fetch_tweets_alternative():
    """Alternative approach with different SSL settings"""
    import ssl
    import certifi
    
    # Use system certificates
    session = requests.Session()
    session.verify = certifi.where()
    
    from twitter_query import TWITTER_QUERY
    
    BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    HEADERS = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    
    PARAMS = {
        'query': TWITTER_QUERY,
        'max_results': 2,
        'tweet.fields': 'public_metrics,created_at,author_id'
    }
    
    url = 'https://api.twitter.com/2/tweets/search/recent'
    
    try:
        resp = session.get(url, headers=HEADERS, params=PARAMS, timeout=30)
        resp.raise_for_status()
        print("Alternative SSL approach successful!")
        
        js = resp.json()
        print(f"Retrieved {len(js.get('data', []))} tweets")
        return js
        
    except Exception as e:
        print(f"Alternative approach also failed: {e}")
        return None

if __name__ == "__main__":
    fetch_tweets()