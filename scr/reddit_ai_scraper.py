import requests
import json
import pandas as pd
import time
from datetime import datetime
from twitter_query import MIN_RETWEETS, MIN_LIKES

def fetch_reddit_posts(subreddit, search_terms, limit=25):
    """Fetch Reddit posts about AI research"""
    
    # Reddit JSON API endpoint
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    
    # Search query
    query = " OR ".join(search_terms)
    
    params = {
        'q': query,
        'restrict_sr': 'on',  # Search within subreddit
        'sort': 'hot',        # Sort by hot posts
        'limit': limit,
        't': 'week'          # Time filter: week
    }
    
    headers = {
        'User-Agent': 'AI Research Scraper 1.0'
    }
    
    try:
        print(f"Fetching from r/{subreddit} with query: {query}")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        posts = data.get('data', {}).get('children', [])
        
        print(f"Found {len(posts)} posts in r/{subreddit}")
        return posts
        
    except Exception as e:
        print(f"Error fetching from r/{subreddit}: {e}")
        return []

def parse_reddit_posts(posts, min_score=100):
    """Parse Reddit posts and filter by engagement"""
    
    parsed_posts = []
    
    for post in posts:
        try:
            post_data = post.get('data', {})
            
            # Extract post info
            title = post_data.get('title', '')
            selftext = post_data.get('selftext', '')
            url = post_data.get('url', '')
            score = post_data.get('score', 0)
            num_comments = post_data.get('num_comments', 0)
            created = post_data.get('created_utc', 0)
            author = post_data.get('author', '')
            subreddit = post_data.get('subreddit', '')
            permalink = f"https://reddit.com{post_data.get('permalink', '')}"
            
            # Convert timestamp
            created_date = datetime.fromtimestamp(created).strftime('%Y-%m-%d %H:%M:%S')
            
            # Filter by engagement (using score as proxy for retweets/likes)
            if score >= min_score:
                parsed_posts.append({
                    'title': title,
                    'text': selftext[:500] if selftext else title,  # Truncate long text
                    'url': url,
                    'score': score,
                    'comments': num_comments,
                    'author': author,
                    'subreddit': subreddit,
                    'created': created_date,
                    'permalink': permalink
                })
                
        except Exception as e:
            print(f"Error parsing post: {e}")
            continue
    
    return parsed_posts

def scrape_ai_research_reddit():
    """Main function to scrape AI research from multiple subreddits"""
    
    # Target subreddits for AI research
    subreddits = [
        'MachineLearning',
        'artificial', 
        'OpenAI',
        'singularity',
        'tech',
        'ChatGPT',
        'LocalLLaMA'
    ]
    
    # Search terms related to your query
    search_terms = [
        'AI research',
        'LLM',
        'model release',
        'AI launch',
        'research paper',
        'breakthrough',
        'new model'
    ]
    
    all_posts = []
    
    for subreddit in subreddits:
        posts = fetch_reddit_posts(subreddit, search_terms, limit=25)
        if posts:
            parsed = parse_reddit_posts(posts, min_score=50)  # Lower threshold for Reddit
            all_posts.extend(parsed)
            
        # Rate limiting
        time.sleep(1)
    
    if not all_posts:
        print("No posts found meeting criteria")
        return
    
    # Create DataFrame and sort by engagement
    df = pd.DataFrame(all_posts)
    df = df.sort_values(['score', 'comments'], ascending=False)
    
    # Remove duplicates based on title similarity
    df = df.drop_duplicates(subset=['title'], keep='first')
    
    print(f"\nFound {len(df)} high-engagement posts")
    
    # Save results
    import os
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/reddit_ai_research.csv', index=False)
    
    print(f"Saved to data/reddit_ai_research.csv")
    
    # Display top results
    print(f"\nTop AI research discussions:")
    for idx, row in df.head(10).iterrows():
        print(f"\n- r/{row['subreddit']} | Score: {row['score']} | Comments: {row['comments']}")
        print(f"  {row['title']}")
        print(f"  {row['permalink']}")

def fetch_hacker_news():
    """Alternative: Fetch from Hacker News"""
    
    print("\n=== Fetching from Hacker News ===")
    
    # HN Algolia API
    url = "https://hn.algolia.com/api/v1/search"
    
    params = {
        'query': 'AI research OR LLM OR "machine learning"',
        'tags': 'story',
        'hitsPerPage': 50,
        'numericFilters': 'points>50,num_comments>10'  # High engagement filter
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        hits = data.get('hits', [])
        
        print(f"Found {len(hits)} HN stories")
        
        hn_posts = []
        for hit in hits:
            hn_posts.append({
                'title': hit.get('title', ''),
                'text': hit.get('title', ''),  # HN doesn't have post text
                'url': hit.get('url', ''),
                'score': hit.get('points', 0),
                'comments': hit.get('num_comments', 0),
                'author': hit.get('author', ''),
                'source': 'HackerNews',
                'created': hit.get('created_at', ''),
                'permalink': f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
            })
        
        if hn_posts:
            df_hn = pd.DataFrame(hn_posts)
            df_hn.to_csv('data/hackernews_ai_research.csv', index=False)
            print("Saved HN results to data/hackernews_ai_research.csv")
            
            print(f"\nTop HN AI stories:")
            for idx, row in df_hn.head(5).iterrows():
                print(f"- {row['score']} pts | {row['title']}")
        
    except Exception as e:
        print(f"Error fetching HN: {e}")

if __name__ == "__main__":
    print("=== Alternative AI Research Data Sources ===")
    
    # Try Reddit first
    scrape_ai_research_reddit()
    
    # Try Hacker News
    fetch_hacker_news()
    
    print("\nDone! Check data/ folder for results.")