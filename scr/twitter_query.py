# twitter_query.py
# Standalone Twitter search query configuration

# Core AI research query - single line format
TWITTER_QUERY = '("AI" OR "LLM") AND ("research" OR "researching") AND ("product" OR "feature" OR "tool" OR "model" OR "launch" OR "launched" OR "launching" OR "release" OR "released" OR "releasing" OR "announce" OR "announced" OR "announcing" OR "introduce" OR "introduced" OR "introducing" OR "unveil" OR "unveiled" OR "unveiling") lang:en -is:retweet'

# Query parameters - conserving API quota
QUERY_PARAMS = {
    'max_results': 10,
    'tweet.fields': 'public_metrics,created_at,author_id,context_annotations'
}

# Engagement thresholds
MIN_RETWEETS = 100
MIN_LIKES = 1000

# Alternative queries for different research focuses
ALT_QUERIES = {
    'breakthrough': '("AI breakthrough" OR "LLM breakthrough" OR "AI discovery") lang:en -is:retweet',
    'companies': '("OpenAI" OR "Anthropic" OR "Google AI" OR "Meta AI") AND ("research" OR "model") lang:en -is:retweet',
    'academic': '("AI paper" OR "ML paper" OR "arxiv" OR "conference") AND ("published" OR "accepted") lang:en -is:retweet'
}