"""
[OK] Deamon Dev's Sentiment Analysis Agent
Built with love by Deamon Dev [ROCKET]

SentimentAnalysisAgent monitors social media sentiment using Claude Code Sub-Agents.
It analyzes sentiment and provides trading signals based on market emotion.

Version 2.0: Utilise Claude Code Sub-Agents exclusively (no external APIs)
"""

# Configuration
TOKENS_TO_TRACK = ["solana", "bitcoin", "ethereum"]  # Add tokens you want to track
TWEETS_PER_RUN = 30  # Number of tweets to collect per run
DATA_FOLDER = "src/data/sentiment"  # Where to store sentiment data
SENTIMENT_HISTORY_FILE = (
    "src/data/sentiment_history.csv"  # Store sentiment scores over time
)
IGNORE_LIST = ["t.co", "discord", "join", "telegram", "discount", "pay"]
CHECK_INTERVAL_MINUTES = 15  # How often to run sentiment analysis

# Sentiment Analysis Prompt for Claude Sub-Agent
SENTIMENT_ANALYSIS_PROMPT = """
You are Deamon Dev's Sentiment Analysis Assistant

Analyze the following social media data and provide sentiment-based trading signals:

Social Media Data:
{sentiment_data}

Market Context:
{market_context}

Token: {token}

Evaluate:
1. Overall sentiment (VERY_BEARISH/BEARISH/NEUTRAL/BULLISH/VERY_BULLISH)
2. Sentiment strength (0-100%)
3. Trading signal (BUY/SELL/HOLD)
4. Confidence level (0-100%)
5. Key emotional indicators

Respond in this format:
1. First line: sentiment label
2. Sentiment strength: X%
3. Action: BUY/SELL/HOLD
4. Confidence: X%
5. Key factors:
6. Risk assessment
"""

import asyncio
import json
import os
import pathlib
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from random import randint

import httpx
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from termcolor import cprint

from src.agents.base_agent import BaseAgent
from src.config import *

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Create data directory if it doesn't exist
pathlib.Path(DATA_FOLDER).mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv()

# Patch httpx
original_client = httpx.Client


def patched_client(*args, **kwargs):
    # Add browser-like headers
    if "headers" not in kwargs:
        kwargs["headers"] = {}

    # List of common user agents
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ]

    kwargs["headers"].update(
        {
            "User-Agent": user_agents[randint(0, len(user_agents) - 1)],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
        }
    )

    kwargs.pop("proxy", None)
    return original_client(*args, **kwargs)


httpx.Client = patched_client

# imports
from twikit import Client, TooManyRequests

class SentimentAnalysisAgent(BaseAgent):
    def __init__(self):
        """Initialize the Sentiment Analysis Agent"""
        super().__init__("sentiment", enable_postgres=True)

        # Configuration pour le sub-agent
        self.subagent_name = "claude-sentiment-advisor"

        self.audio_dir = Path("src/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        # Initialize sentiment history file
        if not os.path.exists(SENTIMENT_HISTORY_FILE):
            pd.DataFrame(columns=["timestamp", "sentiment_score", "num_tweets"]).to_csv(
                SENTIMENT_HISTORY_FILE, index=False
            )

        cprint(
            "[OK] Sentiment Analysis Agent initialized with Claude Code Sub-Agents!",
            "white",
            "on_blue",
        )

    def call_subagent(self, prompt: str, context_data: dict = None) -> str:
        """
        Appeler le sub-agent claude-sentiment-advisor via Claude Code CLI

        Args:
            prompt: Le prompt pour le sub-agent
            context_data: Données contextuelles (sentiment scores, market data, etc.)

        Returns:
            Réponse du sub-agent

        Raises:
            RuntimeError: Si l'appel au sub-agent échoue
        """
        import json
        import subprocess

        full_prompt = f"""Use the claude-sentiment-advisor subagent to analyze this sentiment scenario:

{prompt}

Context Data:
{json.dumps(context_data, indent=2) if context_data else 'N/A'}

Please provide a detailed sentiment analysis with clear trading recommendations (BUY/SELL/HOLD/WATCH)."""

        # Exécuter Claude Code avec le sub-agent
        cmd = [
            "claude",
            "--dangerously-skip-permissions",
            "--agent",
            "claude-sentiment-advisor",
            full_prompt,
        ]

        cprint(
            f"[INFO] Calling sub-agent: claude-sentiment-advisor (skipping permissions)",
            "cyan",
        )

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minutes timeout
            cwd=os.getcwd(),
        )

        if result.returncode != 0:
            error_msg = f"[ERROR] Sub-agent error: {result.stderr}"
            cprint(error_msg, "red")
            raise RuntimeError(error_msg)

        cprint("[OK] Sub-agent response received", "green")
        return result.stdout

    def analyze_sentiment_with_subagent(
        self, sentiment_score: float, num_tweets: int, token: str
    ) -> dict:
        """
        Analyser le sentiment avec sub-agent pour génération de signaux de trading

        Args:
            sentiment_score: Score de sentiment (-1 à 1)
            num_tweets: Nombre de tweets analysés
            token: Token analyzed

        Returns:
            Dictionnaire avec recommandation et analyse

        Raises:
            RuntimeError: Si l'appel au sub-agent échoue
        """
        # Déterminer le niveau de sentiment
        if sentiment_score <= -0.6:
            sentiment_level = "EXTREME FEAR"
        elif sentiment_score <= -0.4:
            sentiment_level = "HIGH FEAR"
        elif sentiment_score < 0.4:
            sentiment_level = "NEUTRAL"
        elif sentiment_score < 0.6:
            sentiment_level = "HIGH GREED"
        else:
            sentiment_level = "EXTREME GREED"

        # Construire le prompt
        prompt = f"""
Analyze sentiment for {token}:
- Sentiment Score: {sentiment_score:.2f} (range: -1.0 to 1.0)
- Sentiment Level: {sentiment_level}
- Number of Tweets: {num_tweets}
- Threshold for Alerts: ±{SENTIMENT_ANNOUNCE_THRESHOLD}

Remember:
- Extreme fear (below -0.4) often signals buy opportunities (contrarian)
- Extreme greed (above 0.4) often signals sell opportunities (contrarian)
- Combine sentiment with market context
- High mention volume strengthens signals
"""

        # Préparer les données contextuelles
        context_data = {
            "token": token,
            "sentiment_score": sentiment_score,
            "sentiment_level": sentiment_level,
            "num_tweets": num_tweets,
            "threshold": SENTIMENT_ANNOUNCE_THRESHOLD,
        }

        cprint(f"[AI] Using Sub-Agent for sentiment signal generation...", "cyan")

        # Appeler le sub-agent
        response = self.call_subagent(prompt, context_data)

        # Parse réponse du sub-agent
        lines = response.split("\n")
        action = "HOLD"  # Default
        confidence = 50

        for line in lines:
            line = line.strip().upper()
            if "ACTION:" in line:
                if "BUY" in line:
                    action = "BUY"
                elif "SELL" in line:
                    action = "SELL"
                elif "HOLD" in line:
                    action = "HOLD"
                elif "WATCH" in line:
                    action = "WATCH"
            elif "CONFIDENCE:" in line:
                import re

                matches = re.findall(r"(\d+)", line)
                if matches:
                    confidence = int(matches[0])

        return {
            "action": action,
            "confidence": confidence,
            "sentiment_score": sentiment_score,
            "sentiment_level": sentiment_level,
            "analysis": response,
            "source": "subagent",
        }

    def analyze_sentiment(self, texts):
        """Analyze sentiment of a batch of texts using Claude Sub-Agent"""
        if not texts:
            return 0.0

        # Prepare the text data for the sub-agent
        text_sample = "\n".join([f"- {text[:200]}" for text in texts[:20]])

        # Prepare the prompt
        prompt = f"""
Analyze the sentiment of these social media texts and return a score from -1 to 1:

{text_sample}

Return ONLY a number between -1 and 1 where:
-1 = Very Bearish/Negative
0 = Neutral
1 = Very Bullish/Positive

Do not include any other text, just the number.
"""

        try:
            # Call the Claude sub-agent
            response = self.call_subagent(prompt, {"num_texts": len(texts)})

            # Parse the response to get a numeric score
            try:
                # Extract the first number from the response
                import re
                match = re.search(r'-?\d+\.?\d*', response.strip())
                if match:
                    score = float(match.group())
                    # Clamp the score to -1 to 1 range
                    return max(-1.0, min(1.0, score))
            except:
                pass

            # Default to neutral if parsing fails
            return 0.0

        except Exception as e:
            cprint(f"[ERROR] Error analyzing sentiment: {str(e)}", "red")
            return 0.0

    def _announce(self, message, is_important=False):
        """Announce a message to console (TTS removed - using Claude Sub-Agent only)"""
        try:
            print(f"\n[ANNOUNCEMENT] {message}")

            # Only add extra formatting for important messages
            if is_important:
                print("=" * 80)

        except Exception as e:
            print(f"[ERROR] Error in announcement: {str(e)}")

    def save_sentiment_score(self, sentiment_score, num_tweets):
        """Save sentiment score to history"""
        try:
            new_data = pd.DataFrame(
                [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "sentiment_score": sentiment_score,
                        "num_tweets": num_tweets,
                    }
                ]
            )

            # Load existing data
            if os.path.exists(SENTIMENT_HISTORY_FILE):
                history_df = pd.read_csv(SENTIMENT_HISTORY_FILE)
                # Convert timestamps to datetime for comparison
                history_df["timestamp"] = pd.to_datetime(history_df["timestamp"])
                # Keep only last 24 hours of data
                cutoff_time = datetime.now() - timedelta(hours=24)
                history_df = history_df[history_df["timestamp"] > cutoff_time]
                # Convert back to ISO format for consistent storage
                history_df["timestamp"] = history_df["timestamp"].dt.isoformat()
                # Append new data
                history_df = pd.concat([history_df, new_data], ignore_index=True)
            else:
                history_df = new_data

            history_df.to_csv(SENTIMENT_HISTORY_FILE, index=False)

        except Exception as e:
            cprint(f"[ERROR] Error saving sentiment history: {str(e)}", "red")

    def get_sentiment_change(self):
        """Calculate sentiment change from last run"""
        try:
            if not os.path.exists(SENTIMENT_HISTORY_FILE):
                return None, None

            history_df = pd.read_csv(SENTIMENT_HISTORY_FILE)
            if len(history_df) < 2:
                return None, None

            # Convert timestamps using ISO format
            history_df["timestamp"] = pd.to_datetime(
                history_df["timestamp"], format="ISO8601"
            )
            history_df = history_df.sort_values("timestamp")

            current_score = float(history_df.iloc[-1]["sentiment_score"])
            previous_score = float(history_df.iloc[-2]["sentiment_score"])

            # Calculate time difference in minutes
            time_diff = (
                history_df.iloc[-1]["timestamp"] - history_df.iloc[-2]["timestamp"]
            ).total_seconds() / 60

            # Calculate percentage change relative to the scale (-1 to 1)
            # Convert to 0-100 scale for easier understanding
            current_percent = (current_score + 1) * 50
            previous_percent = (previous_score + 1) * 50
            percent_change = current_percent - previous_percent

            return percent_change, time_diff

        except Exception as e:
            cprint(f"[ERROR] Error calculating sentiment change: {str(e)}", "red")
            return None, None

    def analyze_and_announce_sentiment(self, tweets):
        """Analyze sentiment of tweets and announce results"""
        if not tweets:
            return

        # Extract text from tweets
        texts = [tweet.text for tweet in tweets]

        # Get sentiment score
        sentiment_score = self.analyze_sentiment(texts)

        # Save score to history
        self.save_sentiment_score(sentiment_score, len(texts))

        # Get change since last run
        percent_change, time_diff = self.get_sentiment_change()

        # Convert score to human readable format
        if sentiment_score > 0.3:
            sentiment = "very positive"
        elif sentiment_score > 0:
            sentiment = "slightly positive"
        elif sentiment_score > -0.3:
            sentiment = "slightly negative"
        else:
            sentiment = "very negative"

        # Format the score as a percentage for easier understanding
        score_percent = (sentiment_score + 1) * 50  # Convert -1 to 1 into 0 to 100

        # Prepare announcement
        message = (
            f"Deamon Dev's Sentiment Analysis: After analyzing {len(texts)} tweets, "
        )
        message += f"the crypto sentiment is {sentiment} "
        message += f"with a score of {score_percent:.1f} out of 100"

        # Add change information if available
        if percent_change is not None and time_diff is not None:
            direction = "up" if percent_change > 0 else "down"
            message += (
                f". Sentiment has moved {direction} {abs(percent_change):.1f} points "
            )
            message += f"over the past {int(time_diff)} minutes"

            # Add percentage interpretation
            if abs(percent_change) > 10:
                message += (
                    f" - this is a significant {abs(percent_change):.1f}% change!"
                )
            elif abs(percent_change) > 5:
                message += f" - a moderate {abs(percent_change):.1f}% shift"
            else:
                message += f" - a small {abs(percent_change):.1f}% change"

        message += "."

        # Announce with voice if sentiment is significant or if there's a big change
        is_important = abs(sentiment_score) > SENTIMENT_ANNOUNCE_THRESHOLD or (
            percent_change is not None and abs(percent_change) > 5
        )
        self._announce(message, is_important)

        # If not announcing vocally, print the raw score for debugging
        if not is_important:
            cprint(
                f"[STATS] Raw sentiment score: {sentiment_score:.2f} (on scale of -1 to 1)",
                "cyan",
            )

    def init_twitter_client(self):
        """Initialize Twitter client using saved cookies"""
        try:
            if not os.path.exists("cookies.json"):
                cprint(
                    "[ERROR] No cookies.json found! Please run twitter_login.py first",
                    "red",
                )
                sys.exit(1)

            cprint("[OK] Deamon Dev's Sentiment Analysis Agent starting up...", "cyan")
            client = Client()
            client.load_cookies("cookies.json")
            cprint(
                "[ROCKET] Deamon Dev's cookies loaded successfully! Time to fly to the moon! [OK]",
                "green",
            )
            return client

        except Exception as e:
            cprint(f"[ERROR] Error initializing client: {str(e)}", "red")
            if os.path.exists("cookies.json"):
                os.remove("cookies.json")
                cprint("[TRASH] Removed invalid cookies file", "yellow")
                cprint("[REFRESH] Please run twitter_login.py again", "yellow")
            sys.exit(1)

    async def get_tweets(self, query):
        """Get tweets with proper error handling"""
        collected_tweets = []

        try:
            cprint(
                f"🕒 Time is {datetime.now()} - Deamon Dev getting fresh tweets for {query}! [STAR2]",
                "cyan",
            )

            # Random delay before request (1-3 seconds)
            time.sleep(randint(1, 3))

            # Get tweets using search
            tweets = await self.client.search_tweet(query, product="Latest")

            if tweets:
                # Process tweets
                for tweet in tweets:
                    if len(collected_tweets) >= TWEETS_PER_RUN:
                        break
                    if not any(
                        word.lower() in tweet.text.lower() for word in IGNORE_LIST
                    ):
                        collected_tweets.append(tweet)
                        cprint(f"[NOTE] Found tweet: {tweet.text[:100]}...", "cyan")

                # Try to get more tweets if we need them
                try:
                    while len(collected_tweets) < TWEETS_PER_RUN:
                        # Random delay between requests (2-5 seconds)
                        time.sleep(randint(2, 5))
                        more_tweets = await tweets.next()
                        if not more_tweets:
                            break

                        for tweet in more_tweets:
                            if len(collected_tweets) >= TWEETS_PER_RUN:
                                break
                            if not any(
                                word.lower() in tweet.text.lower()
                                for word in IGNORE_LIST
                            ):
                                collected_tweets.append(tweet)
                                cprint(
                                    f"[NOTE] Found tweet: {tweet.text[:100]}...", "cyan"
                                )
                except AttributeError:
                    # If pagination is not supported, just continue with what we have
                    cprint("[STATS] Got initial batch of tweets", "cyan")
                except Exception as e:
                    cprint(f"ℹ️ Stopped pagination: {str(e)}", "yellow")

        except TooManyRequests as e:
            rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
            wait_time = (rate_limit_reset - datetime.now()).total_seconds() + randint(
                5, 10
            )
            cprint(f"[CLOCK] Rate limit hit, waiting {wait_time} seconds...", "yellow")
            time.sleep(wait_time)
            # Try one more time after waiting
            try:
                tweets = await self.client.search_tweet(query, product="Latest")
                if tweets:
                    for tweet in tweets:
                        if len(collected_tweets) >= TWEETS_PER_RUN:
                            break
                        if not any(
                            word.lower() in tweet.text.lower() for word in IGNORE_LIST
                        ):
                            collected_tweets.append(tweet)
                            cprint(f"[NOTE] Found tweet: {tweet.text[:100]}...", "cyan")
            except Exception as e:
                cprint(f"[ERROR] Second attempt failed: {str(e)}", "red")
        except Exception as e:
            cprint(f"[ERROR] Error fetching tweets: {str(e)}", "red")
            time.sleep(randint(3, 7))

        if collected_tweets:
            cprint(
                f"[OK] Successfully collected {len(collected_tweets)} tweets for {query}",
                "green",
            )
        else:
            cprint(f"[WARNING] No tweets found for {query}", "yellow")

        return collected_tweets

    def save_tweets(self, tweets, token):
        """Save tweets to CSV file using pandas, appending new ones and avoiding duplicates"""
        filename = f"{DATA_FOLDER}/{token}_tweets.csv"

        # Prepare new tweets data
        new_tweets_data = []
        for tweet in tweets:
            if not hasattr(tweet, "id"):
                continue

            try:
                tweet_data = {
                    "collection_time": datetime.now().isoformat(),
                    "tweet_id": str(tweet.id),
                    "created_at": tweet.created_at,
                    "user_name": tweet.user.name,
                    "user_id": str(tweet.user.id),
                    "text": tweet.text,
                    "retweet_count": tweet.retweet_count,
                    "favorite_count": tweet.favorite_count,
                    "reply_count": tweet.reply_count,
                    "quote_count": getattr(tweet, "quote_count", 0),
                    "language": getattr(tweet, "lang", "unknown"),
                }
                new_tweets_data.append(tweet_data)
            except Exception as e:
                cprint(f"[WARNING] Error processing tweet: {str(e)}", "yellow")
                continue

        if not new_tweets_data:
            cprint("ℹ️ No new tweets to save", "yellow")
            return

        # Convert to DataFrame
        new_df = pd.DataFrame(new_tweets_data)

        try:
            # Load existing data if file exists
            if os.path.exists(filename):
                existing_df = pd.read_csv(filename)
                # Remove duplicates based on tweet_id
                new_df = new_df[~new_df["tweet_id"].isin(existing_df["tweet_id"])]
                # Append new data
                if not new_df.empty:
                    pd.concat([existing_df, new_df], ignore_index=True).to_csv(
                        filename, index=False
                    )
            else:
                # Save new file
                new_df.to_csv(filename, index=False)

            cprint(
                f"[NOTE] Added {len(new_df)} new tweets to {token}_tweets.csv", "green"
            )
            if os.path.exists(filename):
                total_tweets = len(pd.read_csv(filename))
                cprint(f"[STATS] Total tweets in database: {total_tweets}", "green")

        except Exception as e:
            cprint(f"[ERROR] Error saving to CSV: {str(e)}", "red")

    async def run_async(self):
        """Async function to run sentiment analysis"""
        cprint("[AI] Deamon Dev's Sentiment Analysis running...", "cyan")

        # Initialize client if not already done
        if not self.client:
            self.client = self.init_twitter_client()

        all_tweets = []
        for token in TOKENS_TO_TRACK:
            try:
                cprint(f"[SEARCH] Analyzing sentiment for {token}...", "cyan")
                tweets = await self.get_tweets(token)
                if tweets:
                    self.save_tweets(tweets, token)
                    all_tweets.extend(tweets)
                    cprint(f"[OK] Saved {len(tweets)} tweets for {token}", "green")
                else:
                    cprint(f"[WARNING] No tweets found for {token}", "yellow")

            except Exception as e:
                cprint(f"[ERROR] Error processing {token}: {str(e)}", "red")
                continue

        # Analyze sentiment for all collected tweets
        if all_tweets:
            self.analyze_and_announce_sentiment(all_tweets)

        cprint("[OK] Deamon Dev's Sentiment Analysis complete! [ROCKET]", "green")

    def run(self):
        """Main function to run sentiment analysis"""
        asyncio.run(self.run_async())


if __name__ == "__main__":
    try:
        agent = SentimentAnalysisAgent()
        cprint(
            f"\n[OK] Deamon Dev's Sentiment Analysis Agent starting (checking every {CHECK_INTERVAL_MINUTES} minutes)...",
            "cyan",
        )

        while True:
            try:
                agent.run()
                next_run = datetime.now() + timedelta(minutes=CHECK_INTERVAL_MINUTES)
                cprint(
                    f"\n😴 Next sentiment check at {next_run.strftime('%H:%M:%S')}",
                    "cyan",
                )
                time.sleep(60 * CHECK_INTERVAL_MINUTES)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                cprint(f"\n[ERROR] Error in run loop: {str(e)}", "red")
                time.sleep(60)  # Wait a minute before retrying

    except KeyboardInterrupt:
        cprint(
            "\n👋 Deamon Dev's Sentiment Analysis Agent shutting down gracefully...",
            "yellow",
        )
    except Exception as e:
        cprint(f"\n[ERROR] Fatal error: {str(e)}", "red")
        sys.exit(1)
