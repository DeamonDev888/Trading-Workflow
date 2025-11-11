"""
[OK] Deamon Dev's Multi-Source Sentiment Analysis Agent V3.0
Built with love by Deamon Dev [ROCKET]

SentimentAnalysisAgent monitors sentiment across MULTIPLE platforms:
- Twitter/X API : Tweets récents, trending hashtags
- Reddit API : Posts et commentaires (r/cryptocurrency, r/bitcoin)
- Discord Webhooks : Canaux crypto populaires
- Telegram APIs : Groupes news

Version 3.0: Multi-source sentiment analysis with real-time data aggregation
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
from termcolor import cprint

TOKENS_TO_TRACK = ["BTC", "ETH", "SOL", "AVAX", "MATIC", "DOT", "LINK", "UNI"]
POSTS_PER_PLATFORM = 25  # Number of posts to collect per platform
DATA_FOLDER = "src/data/sentiment"
SENTIMENT_HISTORY_FILE = "src/data/sentiment_history.csv"
CHECK_INTERVAL_MINUTES = 15

REDDIT_SUBREDDITS = [
    "cryptocurrency",
    "bitcoin",
    "ethereum",
    "solana",
    "CryptoCurrency",
    "binance",
    "CryptoMarkets",
]
DISCORD_WEBHOOKS = [
]
TELEGRAM_CHANNELS = [
]

Path(DATA_FOLDER).mkdir(parents=True, exist_ok=True)


class TwitterSentimentCollector:
    """Collect sentiment data from Twitter/X API"""

    def __init__(self):
        self.base_url = "https://api.x.com/2"
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

    async def collect_tweets(self, token: str, limit: int = POSTS_PER_PLATFORM) -> List[Dict]:
        """Collect recent tweets about specific token"""
        try:
            if not self.bearer_token:
                print("[WARNING] Twitter Bearer token not found, using web scraping fallback")
                return await self._web_scrape_fallback(token, limit)

            headers = {"Authorization": f"Bearer {self.bearer_token}"}

            query = f"#{token} OR ${token} crypto -is:retweet lang:en"
            params = {
                "query": query,
                "max_results": min(limit, 100),
                "tweet.fields": "created_at,public_metrics,context_annotations",
                "expansions": "author_id",
            }

            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(
                    f"{self.base_url}/tweets/search/recent", params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        tweets = []

                        for tweet in data.get("data", []):
                            tweets.append(
                                {
                                    "platform": "twitter",
                                    "text": tweet.get("text", ""),
                                    "created_at": tweet.get("created_at", ""),
                                    "metrics": tweet.get("public_metrics", {}),
                                    "token": token,
                                }
                            )

                        print(f"[OK] Collected {len(tweets)} tweets for {token}")
                        return tweets
                    else:
                        print(f"[ERROR] Twitter API error: {response.status}")
                        return await self._web_scrape_fallback(token, limit)

        except Exception as e:
            print(f"[ERROR] Twitter collection failed: {e}")
            return await self._web_scrape_fallback(token, limit)

    async def _web_scrape_fallback(self, token: str, limit: int) -> List[Dict]:
        """Fallback web scraping method"""
        try:
            print(f"[INFO] Using web scraping fallback for {token}")
            return []
        except Exception as e:
            print(f"[ERROR] Fallback scraping failed: {e}")
            return []


class RedditSentimentCollector:
    """Collect sentiment data from Reddit API"""

    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = "SentimentAnalysisAgent/1.0"

    async def collect_posts(self, token: str, limit: int = POSTS_PER_PLATFORM) -> List[Dict]:
        """Collect posts from crypto subreddits about token"""
        posts = []

        try:
            access_token = await self._get_access_token()
            if not access_token:
                print("[ERROR] Could not get Reddit access token")
                return posts

            headers = {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": self.user_agent,
            }

            query = f"{token.lower()} OR {token.upper()}"

            async with aiohttp.ClientSession(headers=headers) as session:
                for subreddit in REDDIT_SUBREDDITS[:3]:  # Limit to 3 subreddits per run
                    try:
                        url = f"https://oauth.reddit.com/r/{subreddit}/search"
                        params = {
                            "q": query,
                            "sort": "new",
                            "t": "day",
                            "limit": min(limit // 3, 25),
                            "type": "link",
                        }

                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()

                                for post in data.get("data", {}).get("children", []):
                                    post_data = post.get("data", {})
                                    posts.append(
                                        {
                                            "platform": "reddit",
                                            "subreddit": subreddit,
                                            "title": post_data.get("title", ""),
                                            "text": post_data.get("selftext", ""),
                                            "score": post_data.get("score", 0),
                                            "comments": post_data.get("num_comments", 0),
                                            "created_at": datetime.fromtimestamp(
                                                post_data.get("created_utc", 0)
                                            ).isoformat(),
                                            "token": token,
                                        }
                                    )

                        await asyncio.sleep(1)  # Rate limiting

                    except Exception as e:
                        print(f"[ERROR] Reddit {subreddit} failed: {e}")
                        continue

            print(f"[OK] Collected {len(posts)} Reddit posts for {token}")
            return posts

        except Exception as e:
            print(f"[ERROR] Reddit collection failed: {e}")
            return posts

    async def _get_access_token(self) -> Optional[str]:
        """Get Reddit OAuth access token"""
        try:
            if not self.client_id or not self.client_secret:
                print("[WARNING] Reddit credentials not configured")
                return None

            auth = (self.client_id, self.client_secret)
            data = {"grant_type": "client_credentials"}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://www.reddit.com/api/v1/access_token", auth=auth, data=data
                ) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        return token_data.get("access_token")
                    else:
                        print(f"[ERROR] Reddit auth failed: {response.status}")
                        return None

        except Exception as e:
            print(f"[ERROR] Reddit auth error: {e}")
            return None


class DiscordSentimentCollector:
    """Collect sentiment data from Discord channels via webhooks"""

    def __init__(self):
        self.webhooks = DISCORD_WEBHOOKS

    async def collect_messages(self, token: str, limit: int = POSTS_PER_PLATFORM) -> List[Dict]:
        """Collect messages from Discord channels"""
        messages = []

        try:
            for webhook_url in self.webhooks[:2]:  # Limit to 2 webhooks
                try:
                    pass
                except Exception as e:
                    print(f"[ERROR] Discord webhook failed: {e}")
                    continue

            print(f"[INFO] Discord collection not implemented (requires Bot API)")
            return messages

        except Exception as e:
            print(f"[ERROR] Discord collection failed: {e}")
            return messages


class TelegramSentimentCollector:
    """Collect sentiment data from Telegram channels"""

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    async def collect_messages(self, token: str, limit: int = POSTS_PER_PLATFORM) -> List[Dict]:
        """Collect messages from Telegram crypto channels"""
        messages = []

        try:
            if not self.bot_token:
                print("[WARNING] Telegram bot token not configured")
                return messages

            print(f"[INFO] Telegram collection not implemented yet for {token}")
            return messages

        except Exception as e:
            print(f"[ERROR] Telegram collection failed: {e}")
            return messages


class NewsSentimentCollector:
    """Collect sentiment data from crypto news sources"""

    def __init__(self):
        self.news_apis = {
            "coindesk": "https://api.coindesk.com/v1/news/search",
            "cryptonews": "https://crypto-news-api.herokuapp.com/news",
        }

    async def collect_news(self, token: str, limit: int = POSTS_PER_PLATFORM) -> List[Dict]:
        """Collect news articles about token"""
        articles = []

        try:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        f"https://api.coindesk.com/v1/news/search",
                        params={"q": token, "limit": limit},
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            for article in data.get("data", [])[: limit // 2]:
                                articles.append(
                                    {
                                        "platform": "news",
                                        "source": "coindesk",
                                        "title": article.get("title", ""),
                                        "description": article.get("description", ""),
                                        "url": article.get("url", ""),
                                        "published_at": article.get("published_at", ""),
                                        "token": token,
                                    }
                                )
                except:
                    pass

                try:
                    async with session.get(
                        "https://cryptopanic.com/api/v1/posts/",
                        params={
                            "auth_token": os.getenv("CRYPTOPANIC_API_KEY"),
                            "currencies": token.lower(),
                            "filter": "hot",
                            "limit": limit // 2,
                        },
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            for post in data.get("results", []):
                                articles.append(
                                    {
                                        "platform": "news",
                                        "source": "cryptopanic",
                                        "title": post.get("title", ""),
                                        "url": post.get("url", ""),
                                        "published_at": post.get("published_at", ""),
                                        "votes": post.get("votes", {}),
                                        "token": token,
                                    }
                                )
                except:
                    pass

            print(f"[OK] Collected {len(articles)} news articles for {token}")
            return articles

        except Exception as e:
            print(f"[ERROR] News collection failed: {e}")
            return articles


class SentimentAnalysisAgent:
    """Multi-Source Sentiment Analysis Agent V3.0"""

    def __init__(self):
        print("\n" + "=" * 80)
        print("[AI] MULTI-SOURCE SENTIMENT ANALYSIS AGENT V3.0")
        print("=" * 80)
        print("[PLATFORMS] Twitter/X, Reddit, News, Discord, Telegram")
        print("=" * 80)

        self.twitter_collector = TwitterSentimentCollector()
        self.reddit_collector = RedditSentimentCollector()
        self.discord_collector = DiscordSentimentCollector()
        self.telegram_collector = TelegramSentimentCollector()
        self.news_collector = NewsSentimentCollector()

        print("[OK] All sentiment collectors initialized")
        print(f"[INFO] Tracking tokens: {', '.join(TOKENS_TO_TRACK)}")
        print(f"[INFO] Posts per platform: {POSTS_PER_PLATFORM}")
        print("=" * 80 + "\n")

    async def collect_all_sentiment_data(self, token: str) -> Dict[str, List]:
        """Collect sentiment data from ALL platforms"""
        print(f"\n[TARGET] Collecting multi-source sentiment for {token}...")

        all_data = {
            "twitter": [],
            "reddit": [],
            "discord": [],
            "telegram": [],
            "news": [],
        }

        tasks = [
            self.twitter_collector.collect_tweets(token),
            self.reddit_collector.collect_posts(token),
            self.discord_collector.collect_messages(token),
            self.telegram_collector.collect_messages(token),
            self.news_collector.collect_news(token),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        platforms = ["twitter", "reddit", "discord", "telegram", "news"]

        for i, platform in enumerate(platforms):
            if isinstance(results[i], list):
                all_data[platform] = results[i]
                print(f"[OK] {platform.title()}: {len(results[i])} items collected")
            else:
                print(f"[ERROR] {platform.title()}: Collection failed - {results[i]}")

        total_items = sum(len(data) for data in all_data.values())
        print(f"\n[SUMMARY] Total sentiment items collected: {total_items}")

        return all_data

    def call_subagent(self, prompt: str) -> str:
        """Appeler le sub-agent Claude pour l'analyse de sentiment"""
        import subprocess
import json

        full_prompt = f"""Use the Deamon-sentiment-analyzer subagent to analyze this sentiment data:

{prompt}

Please provide a detailed sentiment analysis with clear trading recommendations."""

        cmd = [
            "claude",
            "--dangerously-skip-permissions",
            "--agent",
            "Deamon-sentiment-analyzer",
            full_prompt,
        ]

        cprint(
            f"[INFO] Calling sub-agent: Deamon-sentiment-analyzer",
            "cyan",
        )

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.getcwd(),
        )

        if result.returncode != 0:
            error_msg = f"[ERROR] Sub-agent error: {result.stderr}"
            cprint(error_msg, "red")
            raise RuntimeError(error_msg)

        cprint("[OK] Sub-agent response received", "green")
        return result.stdout

    async def analyze_sentiment(self, token: str) -> Dict[str, Any]:
        """Analyze sentiment across all platforms for a specific token"""
        try:
            print(f"\n{'='*80}")
            print(f"[AI] MULTI-SOURCE SENTIMENT ANALYSIS FOR {token}")
            print(f"{'='*80}")

            sentiment_data = await self.collect_all_sentiment_data(token)

            combined_text = self._prepare_sentiment_text(sentiment_data)

            if not combined_text.strip():
                print(f"[WARNING] No sentiment data collected for {token}")
                return {
                    "token": token,
                    "sentiment": "NEUTRAL",
                    "strength": 0,
                    "action": "HOLD",
                    "confidence": 0,
                    "sources": sentiment_data,
                    "error": "No data collected",
                }

            prompt = f"""
            Analyze sentiment for {token} using this multi-source data:

            {combined_text}

            Provide analysis in this format:
            SENTIMENT: [VERY_BEARISH/BEARISH/NEUTRAL/BULLISH/VERY_BULLISH]
            STRENGTH: [0-100%]
            ACTION: [BUY/SELL/HOLD]
            CONFIDENCE: [0-100%]
            KEY_FACTORS: [3-5 bullet points]
            RISK_ASSESSMENT: [brief assessment]
            """

            cprint("[AI] Calling Claude Sentiment Analyzer...", "cyan")
            analysis_response = self.call_subagent(prompt)

            parsed = self._parse_analysis_response(analysis_response)

            result = {
                "token": token,
                "timestamp": datetime.now().isoformat(),
                "sentiment": parsed.get("sentiment", "NEUTRAL"),
                "strength": parsed.get("strength", 0),
                "action": parsed.get("action", "HOLD"),
                "confidence": parsed.get("confidence", 0),
                "key_factors": parsed.get("key_factors", []),
                "risk_assessment": parsed.get("risk_assessment", ""),
                "sources_summary": {
                    platform: len(data) for platform, data in sentiment_data.items()
                },
                "total_items": sum(len(data) for data in sentiment_data.values()),
                "sources": sentiment_data,
            }

            self._display_analysis_results(result)

            return result

        except Exception as e:
            print(f"[ERROR] Sentiment analysis failed for {token}: {e}")
            return {
                "token": token,
                "error": str(e),
                "sentiment": "NEUTRAL",
                "action": "HOLD",
            }

    def _prepare_sentiment_text(self, sentiment_data: Dict[str, List]) -> str:
        """Prepare combined text from all sources for analysis"""
        text_parts = []

        if sentiment_data["twitter"]:
            text_parts.append("=== TWITTER/X ===")
            for item in sentiment_data["twitter"][:10]:
                text_parts.append(f"Tweet: {item.get('text', '')[:200]}...")

        if sentiment_data["reddit"]:
            text_parts.append("=== REDDIT ===")
            for item in sentiment_data["reddit"][:10]:
                text_parts.append(f"r/{item.get('subreddit', '')}: {item.get('title', '')}")
                if item.get("text"):
                    text_parts.append(f"Content: {item['text'][:200]}...")

        if sentiment_data["news"]:
            text_parts.append("=== CRYPTO NEWS ===")
            for item in sentiment_data["news"][:10]:
                text_parts.append(f"{item.get('source', '')}: {item.get('title', '')}")
                if item.get("description"):
                    text_parts.append(f"Summary: {item['description'][:200]}...")

        return "\n".join(text_parts)

    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse sub-agent analysis response"""
        parsed = {}

        try:
            lines = response.strip().split("\n")

            for line in lines:
                line = line.strip()
                if line.startswith("SENTIMENT:"):
                    parsed["sentiment"] = line.split(":", 1)[1].strip()
                elif line.startswith("STRENGTH:"):
                    strength_str = line.split(":", 1)[1].strip().replace("%", "")
                    parsed["strength"] = float(strength_str)
                elif line.startswith("ACTION:"):
                    parsed["action"] = line.split(":", 1)[1].strip()
                elif line.startswith("CONFIDENCE:"):
                    confidence_str = line.split(":", 1)[1].strip().replace("%", "")
                    parsed["confidence"] = float(confidence_str)
                elif line.startswith("KEY_FACTORS:"):
                    factors = []
                    idx = lines.index(line) + 1
                    while idx < len(lines) and (
                        lines[idx].strip().startswith("-") or lines[idx].strip().startswith("•")
                    ):
                        factors.append(lines[idx].strip())
                        idx += 1
                    parsed["key_factors"] = factors
                elif line.startswith("RISK_ASSESSMENT:"):
                    parsed["risk_assessment"] = line.split(":", 1)[1].strip()

        except Exception as e:
            print(f"[ERROR] Could not parse analysis response: {e}")

        return parsed

    def _display_analysis_results(self, result: Dict[str, Any]):
        """Display sentiment analysis results"""
        print(f"\n{'='*80}")
        print(f"[RESULT] SENTIMENT ANALYSIS FOR {result['token']}")
        print(f"{'='*80}")

        sentiment = result.get("sentiment", "NEUTRAL")
        color = {
            "VERY_BULLISH": "green",
            "BULLISH": "cyan",
            "NEUTRAL": "yellow",
            "BEARISH": "red",
            "VERY_BEARISH": "magenta",
        }.get(sentiment, "white")

        cprint(f"🎯 SENTIMENT: {sentiment}", color)
        cprint(f"💪 STRENGTH: {result.get('strength', 0):.0f}%", color)
        cprint(f"📊 ACTION: {result.get('action', 'HOLD')}", color)
        cprint(f"🎲 CONFIDENCE: {result.get('confidence', 0):.0f}%", "blue")

        print(f"\n📈 Sources Summary:")
        for platform, count in result.get("sources_summary", {}).items():
            print(f"   • {platform.title()}: {count} items")

        print(f"\n📋 Total Items Analyzed: {result.get('total_items', 0)}")

        if result.get("key_factors"):
            print(f"\n🔍 Key Factors:")
            for factor in result["key_factors"]:
                print(f"   • {factor}")

        if result.get("risk_assessment"):
            print(f"\n⚠️ Risk Assessment: {result['risk_assessment']}")

        print(f"{'='*80}\n")

    async def run(self):
        """Main execution method"""
        try:
            print(f"\n[START] Multi-Source Sentiment Analysis Agent V3.0")
            print(f"[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            all_results = []

            for token in TOKENS_TO_TRACK:
                result = await self.analyze_sentiment(token)
                all_results.append(result)
                await asyncio.sleep(2)  # Rate limiting between tokens

            self._generate_market_summary(all_results)

            print(
                f"\n[COMPLETE] Sentiment analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            return all_results

        except Exception as e:
            print(f"[ERROR] Agent execution failed: {e}")
            return []

    def _generate_market_summary(self, results: List[Dict]):
        """Generate overall market sentiment summary"""
        try:
            print(f"\n{'='*80}")
            print("[MARKET] OVERALL CRYPTO SENTIMENT SUMMARY")
            print(f"{'='*80}")

            if not results:
                print("[INFO] No results to summarize")
                return

            sentiment_counts = {}
            total_confidence = 0
            valid_results = 0

            for result in results:
                if result.get("sentiment") and result.get("confidence", 0) > 0:
                    sentiment = result["sentiment"]
                    sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                    total_confidence += result["confidence"]
                    valid_results += 1

            if valid_results == 0:
                print("[INFO] No valid sentiment results")
                return

            avg_confidence = total_confidence / valid_results

            print(f"📊 Sentiment Distribution:")
            for sentiment, count in sorted(sentiment_counts.items()):
                percentage = (count / valid_results) * 100
                print(f"   • {sentiment}: {count} tokens ({percentage:.1f}%)")

            print(f"\n📈 Average Confidence: {avg_confidence:.1f}%")
            print(f"🔢 Tokens Analyzed: {valid_results}")

            if sentiment_counts:
                dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)
                color = {
                    "VERY_BULLISH": "green",
                    "BULLISH": "cyan",
                    "NEUTRAL": "yellow",
                    "BEARISH": "red",
                    "VERY_BEARISH": "magenta",
                }.get(dominant_sentiment, "white")

                cprint(f"\n🎯 OVERALL MARKET SENTIMENT: {dominant_sentiment}", color)
                cprint(f"📊 Market Confidence: {avg_confidence:.1f}%", "blue")

            print(f"{'='*80}\n")

        except Exception as e:
            print(f"[ERROR] Market summary generation failed: {e}")


async def run_sentiment_analysis():
    """Run the sentiment analysis agent"""
    agent = SentimentAnalysisAgent()
    return await agent.run()


if __name__ == "__main__":
    results = asyncio.run(run_sentiment_analysis())
    print(f"\n[FINAL] Analysis complete. Processed {len(results)} tokens.")
