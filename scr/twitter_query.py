# twitter_query.py
# Standalone Twitter search query configuration

# Simplified query for both Twitter API and Nitter
TWITTER_QUERY = 'AI research launch release announce lang:en -is:retweet'

# Query parameters - conserving API quota
QUERY_PARAMS = {
    'max_results': 10,
    'tweet.fields': 'public_metrics,created_at,author_id'
}

# Engagement thresholds
MIN_RETWEETS = 100
MIN_LIKES = 1000

# Alternative simple queries that work
ALT_QUERIES = {
    'simple': 'AI research lang:en -is:retweet',
    'launches': 'AI launch lang:en -is:retweet', 
    'releases': 'AI release lang:en -is:retweet'
}