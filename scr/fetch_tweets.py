import os
import requests
import pandas as pd

BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
if not BEARER_TOKEN:
    raise SystemExit('Set TWITTER_BEARER_TOKEN environment variable')

HEADERS = {'Authorization': f'Bearer {BEARER_TOKEN}'}
QUERY = '("AI research" OR "AI deep research" OR "generative AI" OR "AI product" OR "AI feature") lang:en -is:retweet'

PARAMS = {
    'query': QUERY,
    'max_results': 1,
    'tweet.fields': 'public_metrics,created_at,author_id'
}

url = 'https://api.twitter.com/2/tweets/search/recent'
resp = requests.get(url, headers=HEADERS, params=PARAMS, timeout=10)
resp.raise_for_status()
js = resp.json()
rows = []
for tw in js.get('data', []):
    metrics = tw.get('public_metrics', {})
    rows.append({
        'id': tw.get('id'),
        'created_at': tw.get('created_at'),
        'author_id': tw.get('author_id'),
        'text': tw.get('text', '').replace('\n', ' '),
        'retweets': metrics.get('retweet_count'),
        'likes': metrics.get('like_count'),
        'replies': metrics.get('reply_count'),
        'quotes': metrics.get('quote_count')
    })

df = pd.DataFrame(rows)
if not df.empty:
    df.sort_values(['retweets', 'likes'], ascending=False, inplace=True)
    df.to_csv('data/trending_ai_research_tweets.csv', index=False)
    print('Saved', len(df), 'tweets2data/trending_ai_research_tweets.csv')
else:
    print('No tweets found.')
