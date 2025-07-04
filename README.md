# X-AI-deep-research

This repository includes a small utility script for fetching recent
Twitter posts about AI research products. The `fetch_tweets.py` script
uses the Twitter v2 API to collect tweets matching several keywords
related to AI research and product features. Results are sorted by
engagement metrics and written to a CSV file.

## Usage

1. Create a Twitter developer account and obtain a bearer token.
2. Set the environment variable `TWITTER_BEARER_TOKEN` with your token.
3. Run the script:

```bash
python scripts/fetch_tweets.py
```

The resulting file `data/trending_ai_research_tweets.csv` will contain
tweet IDs, timestamps, text, and engagement counts (likes, retweets,
replies, quotes).

A small example dataset is provided at
`data/sample_trending_ai_research_tweets.csv` to illustrate the output
format.
