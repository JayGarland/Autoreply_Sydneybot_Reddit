# Reddit Bot Restructure Implementation Plan

This document provides step-by-step instructions to transform the current monolithic structure into a clean, modular architecture.

## 📋 Overview

**Goal**: Transform the current single-file approach into a maintainable, testable, and scalable modular structure.

**Timeline**: 4-5 weeks (can be done incrementally while keeping the bot running)

**Strategy**: Gradual migration with backward compatibility to ensure zero downtime.

---

## 🎯 Phase 1: Core Refactoring (Week 1-2)

### Step 1.1: Create Directory Structure

```bash
# Create the new directory structure
mkdir bot
mkdir bot\core
mkdir bot\utils
mkdir ai
mkdir ai\providers
mkdir config
mkdir tests
mkdir tests\unit
mkdir tests\integration
mkdir tests\fixtures
mkdir scripts
mkdir docs
```

### Step 1.2: Create **init**.py Files

Create empty `__init__.py` files in all directories:

- `bot\__init__.py`
- `bot\core\__init__.py`
- `bot\utils\__init__.py`
- `ai\__init__.py`
- `ai\providers\__init__.py`
- `config\__init__.py`
- `tests\__init__.py`

### Step 1.3: Extract Content Helper Functions

**File**: `bot\utils\content_helpers.py`

```python
"""Content utility functions for Reddit posts and comments."""
import praw


def get_content_text(content) -> str:
    """Extract text content from submission or comment."""
    return content.selftext if isinstance(content, praw.models.reddit.submission.Submission) else content.body


def is_submission(content) -> bool:
    """Check if content is a submission (post) rather than a comment."""
    return isinstance(content, praw.models.reddit.submission.Submission)


def is_image_url(url: str) -> bool:
    """Check if URL points to an image."""
    return url.lower().endswith((".jpg", ".png", ".jpeg", ".gif"))
```

### Step 1.4: Extract Text Processing Functions

**File**: `bot\utils\text_processing.py`

```python
"""Text processing utilities for bot replies."""
import re
import bleach


def remove_bot_statement(reply: str) -> str:
    """Remove bot statement from the end of reply."""
    return "\n\n".join(reply.strip().split("\n\n")[:-1]).strip()


def remove_extra_format(reply: str) -> str:
    """Remove extra reply formatting."""
    pattern = r'回复[^：]*：(.*)'
    result = re.search(pattern, reply, re.S)
    if result is None:
        return reply
    result = result.group(1).strip()
    if result.startswith(""") and result.endswith("""):
        result = result[1:-1]
    return result


def remove_incomplete_sentence(reply: str) -> str:
    """Remove incomplete sentences from the end of reply."""
    pattern = r"(.*[！!?？。…])"
    result = re.search(pattern, reply, re.S)
    if result is not None:
        return result.group(1).strip()
    else:
        return reply


def concat_reply(former_str: str, latter_str: str) -> str:
    """Concatenate strings, removing duplicate parts at boundaries."""
    former_str = former_str.strip()
    latter_str = latter_str.strip()
    min_length = min(len(former_str), len(latter_str))
    for i in range(min_length, 0, -1):
        if former_str[-i:] == latter_str[:i]:
            return former_str + latter_str[i:]
    return former_str + latter_str


def detect_chinese_char_pair(context, threshold=5):
    """Detect frequent Chinese character pairs in context."""
    freq = {}
    for i in range(len(context) - 1):
        pair = context[i:i+2]
        if '\u4e00' <= pair[0] <= '\u9fff' and '\u4e00' <= pair[1] <= '\u9fff':
            freq[pair] = freq.get(pair, 0) + 1

    for pair, count in freq.items():
        if count >= threshold:
            return True, pair
    return False, None


def clean_and_format_context(context: str) -> str:
    """Clean and format context for AI processing."""
    return "<|im_start|>system\n\n" + bleach.clean(context).strip()


def clean_ask_string(ask_string: str) -> str:
    """Clean ask string for AI processing."""
    return bleach.clean(ask_string).strip()
```

### Step 1.5: Extract Image Helper Functions

**File**: `bot\utils\image_helpers.py`

```python
"""Image processing utilities."""
import requests
from io import BytesIO
from PIL import Image
import re


def get_image_from_url(url: str) -> Image:
    """Download and return PIL Image from URL."""
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img


def extract_image_url_from_content(content) -> str:
    """Extract image URL from Reddit content."""
    from bot.utils.content_helpers import is_submission, is_image_url

    if is_submission(content):
        # Check if submission URL is an image
        url = getattr(content, "url", "")
        if is_image_url(url):
            return url
    else:
        # Check comment body HTML for images
        if hasattr(content, "body_html"):
            m = re.search(r'<img src="(.+?)"', content.body_html)
            if m:
                return m.group(1)

        # Check submission URL if comment belongs to image post
        if hasattr(content, "submission"):
            sub_url = getattr(content.submission, "url", "")
            if is_image_url(sub_url):
                return sub_url

    return None
```

### Step 1.6: Extract Reddit Client

**File**: `bot\core\reddit_client.py`

```python
"""Reddit API client wrapper."""
import praw
import random
from typing import List, Optional
from config import conf
from log import logger


class RedditClient:
    """Wrapper for Reddit API client with bot-specific functionality."""

    def __init__(self):
        self.reddit = None
        self.subreddit = None
        self.current_subreddit_name = None
        self.subreddit_names = []
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Reddit client with credentials."""
        bot_name = conf().get('bot_name')
        password = conf().get('password')
        client_id = conf().get('client_id')
        client_secret = conf().get('client_secret')
        user_agent = "autoreply bot created by u/Chinese_Dictator."

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            password=password,
            user_agent=user_agent,
            username=bot_name
        )

        # Get subreddit names
        target_subreddits = conf().get('TargetSubreddits')
        self.subreddit_names = [list(target_subreddits[i].keys())[0]
                               for i in range(len(target_subreddits))]

        # Set random subreddit
        self.set_random_subreddit()

    def set_random_subreddit(self):
        """Set a random subreddit as current."""
        self.current_subreddit_name = random.choice(self.subreddit_names)
        self.subreddit = self.reddit.subreddit(self.current_subreddit_name)
        logger.info(f"Set current subreddit to: {self.current_subreddit_name}")

    def get_subreddit_config(self) -> dict:
        """Get configuration for current subreddit."""
        for reddit_config in conf().get("TargetSubreddits"):
            if self.current_subreddit_name in reddit_config:
                return reddit_config[self.current_subreddit_name]
        return {}

    def get_comment(self, comment_id: str):
        """Get comment by ID."""
        return self.reddit.comment(comment_id)

    def get_submission(self, submission_id: str):
        """Get submission by ID."""
        return self.reddit.submission(submission_id)

    def get_new_submissions(self, limit: int = 10) -> List:
        """Get new submissions from current subreddit."""
        return list(self.subreddit.new(limit=limit))

    def get_comments(self, limit: int = 50) -> List:
        """Get comments from current subreddit."""
        return list(self.subreddit.comments(limit=limit))
```

### Step 1.7: Extract Content Checker

**File**: `bot\core\content_checker.py`

```python
"""Content validation and checking utilities."""
import re
from typing import Set
from praw.exceptions import ClientException
from bot.utils.content_helpers import get_content_text, is_submission
from config import conf
from log import logger


class ContentChecker:
    """Handles all content validation and checking logic."""

    def __init__(self):
        self.ignored_content: Set[str] = set()
        self.removed_content_list = ["[removed]", "[deleted]", "[ Removed by Reddit ]"]
        self.blocked_content = "[unavailable]"

        # Load config
        self.bot_name = conf().get('bot_name')
        self.bot_name_list = conf().get("bot_account")
        self.ignore_name_list = conf().get("blocked_account")
        self.blacklist = conf().get("blacklist")

    def check_status(self, content) -> str:
        """Check if content status is normal, removed, or blocked."""
        check_str = get_content_text(content)
        if check_str in self.removed_content_list:
            return "removed"
        elif check_str == self.blocked_content:
            return "blocked"
        else:
            return "normal"

    def check_at_me(self, content, bot_nickname: str) -> bool:
        """Check if content mentions the bot."""
        check_str = get_content_text(content)

        # Check if the content author is not the bot name
        if content.author != self.bot_name:
            if (check_str.lower().find(f"u/{self.bot_name}".lower()) != -1 or
                re.search(bot_nickname, check_str) is not None):
                return True

            if is_submission(content):
                if (content.title.lower().find(f"u/{self.bot_name}".lower()) != -1 or
                    re.search(bot_nickname, content.title) is not None):
                    return True
        return False

    def _check_basic_ignore_conditions(self, content) -> bool:
        """Check basic conditions that should cause content to be ignored."""
        # Already processed
        if content.id in self.ignored_content:
            return True

        # Author-based checks
        if content.author in self.blacklist:
            return True

        if content.author == self.bot_name or content.author in self.bot_name_list:
            self.ignored_content.add(content.id)
            return True

        if content.author in self.ignore_name_list:
            self.ignored_content.add(content.id)
            return True

        return False

    def _has_bot_replied(self, content, target_bot_name=None) -> bool:
        """Check if bot has already replied to this content."""
        if target_bot_name is None:
            target_bot_name = self.bot_name

        if is_submission(content):
            content.comments.replace_more(limit=0)
            for comment in content.comments:
                if comment.author == target_bot_name:
                    return True
        else:
            try:
                content.refresh()
            except ClientException as e:
                logger.warning(f"Could not refresh comment {content.id}: {e} -- marking as replied")
                return True

            for reply in content.replies:
                if reply.author == target_bot_name:
                    return True
        return False

    def check_ignored(self, content) -> bool:
        """Check if content should be ignored for random triggers."""
        # Basic ignore conditions
        if self._check_basic_ignore_conditions(content):
            return True

        # Check if any bot has replied (for ignore purposes, check all bots)
        if is_submission(content):
            content.comments.replace_more(limit=0)
            for comment in content.comments:
                if comment.author in self.bot_name_list:
                    self.ignored_content.add(content.id)
                    return True
        else:
            content.refresh()
            for reply in content.replies:
                if reply.author in self.bot_name_list:
                    self.ignored_content.add(content.id)
                    return True
        return False

    def check_replied(self, content) -> bool:
        """Check if content has already been replied to by this bot."""
        # Basic ignore conditions
        if self._check_basic_ignore_conditions(content):
            return True

        # Check if this specific bot has replied
        if self._has_bot_replied(content):
            self.ignored_content.add(content.id)
            return True

        return False

    def load_ignored_content(self, ignored_set: Set[str]):
        """Load previously ignored content from external source."""
        self.ignored_content = ignored_set

    def get_ignored_content(self) -> Set[str]:
        """Get current ignored content set."""
        return self.ignored_content
```

### Step 1.8: Update AIbot_utils.py (Compatibility Layer)

Add at the top of `AIbot_utils.py`:

```python
# Compatibility layer - gradually migrating to modular structure
import os

# Feature flags for gradual migration
USE_NEW_CONTENT_CHECKER = os.getenv("USE_NEW_CONTENT_CHECKER", "false").lower() == "true"
USE_NEW_REDDIT_CLIENT = os.getenv("USE_NEW_REDDIT_CLIENT", "false").lower() == "true"

# Import new modules when enabled
if USE_NEW_CONTENT_CHECKER:
    from bot.core.content_checker import ContentChecker
    _content_checker = ContentChecker()

    # Override old functions with new implementations
    def check_status(content):
        return _content_checker.check_status(content)

    def check_at_me(content, bot_nickname):
        return _content_checker.check_at_me(content, bot_nickname)

    def check_ignored(content):
        return _content_checker.check_ignored(content)

    def check_replied(content):
        return _content_checker.check_replied(content)

if USE_NEW_REDDIT_CLIENT:
    from bot.core.reddit_client import RedditClient
    _reddit_client = RedditClient()

    # Override global reddit instance
    reddit = _reddit_client.reddit
    subreddit = _reddit_client.subreddit
```

---

## 🤖 Phase 2: AI Provider Abstraction (Week 3)

### Step 2.1: Create AI Provider Base Class

**File**: `ai\base.py`

```python
"""Base AI provider interface."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, List


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self._initialize_client()

    @abstractmethod
    def _initialize_client(self):
        """Initialize the AI client."""
        pass

    @abstractmethod
    def generate_reply(
        self,
        system_prompt: str,
        user_prompt: str,
        image_data: Optional[Any] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate a reply using the AI provider."""
        pass

    def health_check(self) -> bool:
        """Check if the AI provider is healthy."""
        try:
            test_response = self.generate_reply("You are a test.", "Say hello.")
            return len(test_response.strip()) > 0
        except Exception:
            return False
```

### Step 2.2: Create Azure Provider

**File**: `ai\providers\azure.py`

```python
"""Azure AI Inference provider."""
from typing import Any, Dict, Optional
from ai.base import AIProvider


class AzureProvider(AIProvider):
    """Azure AI Inference provider implementation."""

    def _initialize_client(self):
        """Initialize Azure client."""
        # Import azure_inference from the existing module
        try:
            from azure_inference import azure_generate_reply
            self._azure_generate_reply = azure_generate_reply
        except ImportError:
            raise ImportError("Azure inference module not available")

    def generate_reply(
        self,
        system_prompt: str,
        user_prompt: str,
        image_data: Optional[Any] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate reply using Azure AI Inference."""
        return self._azure_generate_reply(system_prompt, user_prompt)
```

### Step 2.3: Create Other AI Providers

**File**: `ai\providers\gemini.py`

```python
"""Google Gemini provider."""
from typing import Any, Dict, Optional
from ai.base import AIProvider


class GeminiProvider(AIProvider):
    """Google Gemini provider implementation."""

    def _initialize_client(self):
        """Initialize Gemini client."""
        import google.generativeai as genai
        # Use client from global scope for compatibility
        # TODO: Move to proper config-based initialization
        from AIbot_utils import client
        self.client = client

    def generate_reply(
        self,
        system_prompt: str,
        user_prompt: str,
        image_data: Optional[Any] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate reply using Gemini."""
        model = self.client.GenerativeModel("gemini-pro")
        convo = model.start_chat(history=[])
        full_prompt = f"{system_prompt}\n{user_prompt}"
        response = convo.send_message(full_prompt)
        return response.text
```

**File**: `ai\providers\cohere.py`

```python
"""Cohere provider."""
from typing import Any, Dict, Optional
from ai.base import AIProvider


class CohereProvider(AIProvider):
    """Cohere provider implementation."""

    def _initialize_client(self):
        """Initialize Cohere client."""
        # Use client from global scope for compatibility
        from AIbot_utils import client
        self.client = client

    def generate_reply(
        self,
        system_prompt: str,
        user_prompt: str,
        image_data: Optional[Any] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate reply using Cohere."""
        messages = [{"role": "SYSTEM", "content": system_prompt}]
        query = user_prompt if not image_data else [user_prompt, image_data]

        resp = self.client.chat(
            message=query,
            preamble=system_prompt,
            chat_history=messages,
            temperature=temperature
        )
        return resp.text
```

**File**: `ai\providers\deepseek.py`

```python
"""DeepSeek provider."""
import re
from typing import Any, Dict, Optional
from ai.base import AIProvider


class DeepSeekProvider(AIProvider):
    """DeepSeek provider implementation."""

    def _initialize_client(self):
        """Initialize DeepSeek client."""
        # Use client from global scope for compatibility
        from AIbot_utils import client
        self.client = client

    def generate_reply(
        self,
        system_prompt: str,
        user_prompt: str,
        image_data: Optional[Any] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate reply using DeepSeek."""
        msgs = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        comp = self.client.chat.completions.create(
            model="deepseek-reasoner",
            messages=msgs,
            temperature=temperature
        )

        reply = comp.choices[0].message.content
        # Remove thinking tags
        reply = re.sub(r'<think>.*?</think>', '', reply, flags=re.DOTALL).strip()
        return reply
```

### Step 2.4: Create AI Provider Factory

**File**: `ai\factory.py`

```python
"""AI provider factory."""
from typing import Dict, Any
from ai.base import AIProvider
from ai.providers.azure import AzureProvider
from ai.providers.gemini import GeminiProvider
from ai.providers.cohere import CohereProvider
from ai.providers.deepseek import DeepSeekProvider


class AIProviderFactory:
    """Factory for creating AI providers."""

    _providers = {
        'AZURE': AzureProvider,
        'GEMINI': GeminiProvider,
        'COHERE': CohereProvider,
        'DEEPSEEK': DeepSeekProvider,
    }

    @classmethod
    def create_provider(cls, model_type: str, config: Dict[str, Any] = None) -> AIProvider:
        """Create an AI provider instance."""
        if config is None:
            config = {}

        if model_type not in cls._providers:
            raise ValueError(f"Unsupported AI model: {model_type}")

        provider_class = cls._providers[model_type]
        return provider_class(config)

    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider names."""
        return list(cls._providers.keys())
```

### Step 2.5: Create Reply Generator

**File**: `bot\core\reply_generator.py`

```python
"""Reply generation using AI providers."""
import os
from typing import Optional
from ai.factory import AIProviderFactory
from bot.utils.content_helpers import is_submission
from bot.utils.text_processing import clean_and_format_context, clean_ask_string
from bot.utils.image_helpers import extract_image_url_from_content, get_image_from_url
from config import conf
from log import logger


class ReplyGenerator:
    """Handles reply generation using AI providers."""

    def __init__(self):
        self.ai_model = conf().get("ai_model")
        self.bot_statement = conf().get("bot_statement")
        self.max_retries = 3

        # Initialize AI provider
        self.ai_provider = AIProviderFactory.create_provider(self.ai_model)

    def generate_ask_string(self, content, bot_nickname: str, is_azure: bool = False) -> str:
        """Generate appropriate ask string based on content type."""
        if is_submission(content):
            return f"{bot_nickname}请回复前述{content.author}的帖子。"
        else:
            if is_azure:
                return f"{bot_nickname}请回复。不必介绍你自己，只输出你回复的内容正文。不要排比，不要重复之前回复的内容或格式。"
            else:
                return (
                    f"{bot_nickname}请回复"
                    " 不必介绍你自己，只输出你回复内容的正文。不要排比，不要重复之前回复的内容或格式。"
                )

    def init_systemprompt_bot(self, sub_user_nickname: str, bot_nickname: str, subreddit_name: str) -> str:
        """Initialize system prompt for bot."""
        persona = None
        for setting_pairs in conf().get("customSet"):
            for key, cusprompt in dict(setting_pairs).items():
                if key == subreddit_name:
                    if isinstance(cusprompt, str) and os.path.isfile(cusprompt):
                        with open(cusprompt, 'r', encoding='utf-8') as f:
                            persona = f.read()
                    else:
                        persona = cusprompt
                    break

        if not persona:
            raise ValueError(f"No persona found for subreddit {subreddit_name}. Please check your configuration.")

        try:
            persona = persona.format(n=sub_user_nickname, k=bot_nickname, m=subreddit_name)
        except ValueError as e:
            logger.warning(str(e))
            persona = persona.replace('{', '{{').replace('}', '}}')
            persona = persona.format(n=sub_user_nickname, k=bot_nickname, m=subreddit_name)

        logger.debug("PERSONA:" + persona)
        return persona

    def generate_and_post_reply(
        self,
        content,
        context: str,
        sub_user_nickname: str,
        bot_nickname: str,
        subreddit_name: str,
        retry_count: int = 0
    ):
        """Generate and post a reply to Reddit content."""
        if retry_count > self.max_retries:
            logger.error(f"Failed after maximum retry attempts ({self.max_retries})")
            return

        try:
            # Prepare context and prompts
            system_context = clean_and_format_context(context)
            ask_string = self.generate_ask_string(content, bot_nickname, is_azure=(self.ai_model == 'AZURE'))
            ask_string = clean_ask_string(ask_string)

            # Get persona
            persona = self.init_systemprompt_bot(sub_user_nickname, bot_nickname, subreddit_name)
            full_system_prompt = persona + system_context

            # Handle image if present
            img_url = extract_image_url_from_content(content)
            image_data = None
            if img_url:
                try:
                    image_data = get_image_from_url(img_url)
                    logger.info(f"Image found: {img_url}")
                except Exception as e:
                    logger.warning(f"Failed to load image {img_url}: {e}")

            # Generate reply
            reply = self.ai_provider.generate_reply(
                system_prompt=full_system_prompt,
                user_prompt=ask_string,
                image_data=image_data
            )

            # Ensure bot statement is appended
            bot_statement_formatted = self.bot_statement.format(k=bot_nickname)
            if bot_statement_formatted.strip() not in reply:
                reply = reply.rstrip() + "\n\n" + bot_statement_formatted

            # Post reply
            content.reply(reply)
            logger.info(f"Successfully posted reply to {content.id}")

        except Exception as e:
            logger.warning(f"generate_reply error ({retry_count + 1}/{self.max_retries}): {e}")
            self.generate_and_post_reply(
                content, context, sub_user_nickname, bot_nickname, subreddit_name, retry_count + 1
            )
```

---

## 🔧 Phase 3: Enhanced Configuration (Week 4)

### Step 3.1: Create Configuration Classes

**File**: `config\base.py`

```python
"""Base configuration classes."""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class SubredditConfig:
    """Configuration for a specific subreddit."""
    name: str
    bot_callname: str
    bot_nickname: str
    sub_user_nickname: str
    persona_file: Optional[str] = None
    persona_content: Optional[str] = None

    def get_persona(self) -> str:
        """Get persona content, loading from file if needed."""
        if self.persona_file and os.path.isfile(self.persona_file):
            with open(self.persona_file, 'r', encoding='utf-8') as f:
                return f.read()
        return self.persona_content or ""


@dataclass
class AIConfig:
    """AI model configuration."""
    model_type: str
    temperature: float = 0.7
    max_retries: int = 3
    timeout: int = 30


@dataclass
class RedditConfig:
    """Reddit API configuration."""
    bot_name: str
    password: str
    client_id: str
    client_secret: str
    user_agent: str = "autoreply bot created by u/Chinese_Dictator."


@dataclass
class BotConfig:
    """Main bot configuration."""
    reddit: RedditConfig
    ai: AIConfig
    subreddits: List[SubredditConfig]
    bot_statement: str
    min_char: int
    interval: int
    submission_num: int
    comment_num: int
    comment_rate: float
    random_check_rate: int
    bot_accounts: List[str]
    blocked_accounts: List[str]
    blacklist: List[str]
```

### Step 3.2: Create Configuration Manager

**File**: `config\manager.py`

```python
"""Configuration manager with validation."""
import json
import os
from typing import Dict, Any, List
from config.base import BotConfig, RedditConfig, AIConfig, SubredditConfig


class ConfigManager:
    """Manages bot configuration with validation."""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config: BotConfig = None
        self.load_config()

    def load_config(self):
        """Load configuration from file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            raw_config = json.load(f)

        self.config = self._parse_config(raw_config)
        self._validate_config()

    def _parse_config(self, raw_config: Dict[str, Any]) -> BotConfig:
        """Parse raw configuration into structured objects."""
        # Parse Reddit config
        reddit_config = RedditConfig(
            bot_name=raw_config.get('bot_name'),
            password=raw_config.get('password'),
            client_id=raw_config.get('client_id'),
            client_secret=raw_config.get('client_secret'),
            user_agent=raw_config.get('user_agent', "autoreply bot created by u/Chinese_Dictator.")
        )

        # Parse AI config
        ai_config = AIConfig(
            model_type=raw_config.get('ai_model'),
            temperature=raw_config.get('ai_temperature', 0.7),
            max_retries=raw_config.get('max_retries', 3),
            timeout=raw_config.get('ai_timeout', 30)
        )

        # Parse subreddit configs
        subreddits = []
        for subreddit_data in raw_config.get('TargetSubreddits', []):
            for sub_name, sub_config in subreddit_data.items():
                subreddit = SubredditConfig(
                    name=sub_name,
                    bot_callname=sub_config.get('bot_callname'),
                    bot_nickname=sub_config.get('bot_nickname'),
                    sub_user_nickname=sub_config.get('sub_user_nickname')
                )
                subreddits.append(subreddit)

        return BotConfig(
            reddit=reddit_config,
            ai=ai_config,
            subreddits=subreddits,
            bot_statement=raw_config.get('bot_statement'),
            min_char=raw_config.get('min_char'),
            interval=raw_config.get('interval'),
            submission_num=raw_config.get('submission_num'),
            comment_num=raw_config.get('comment_num'),
            comment_rate=raw_config.get('comment_rate'),
            random_check_rate=raw_config.get('random_check_rate'),
            bot_accounts=raw_config.get('bot_account', []),
            blocked_accounts=raw_config.get('blocked_account', []),
            blacklist=raw_config.get('blacklist', [])
        )

    def _validate_config(self):
        """Validate configuration values."""
        errors = []

        # Validate Reddit config
        if not self.config.reddit.bot_name:
            errors.append("bot_name is required")
        if not self.config.reddit.client_id:
            errors.append("client_id is required")
        if not self.config.reddit.client_secret:
            errors.append("client_secret is required")

        # Validate AI config
        if not self.config.ai.model_type:
            errors.append("ai_model is required")

        # Validate subreddits
        if not self.config.subreddits:
            errors.append("At least one subreddit must be configured")

        for subreddit in self.config.subreddits:
            if not subreddit.name:
                errors.append("Subreddit name is required")
            if not subreddit.bot_nickname:
                errors.append(f"bot_nickname is required for subreddit {subreddit.name}")

        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")

    def get_subreddit_config(self, subreddit_name: str) -> SubredditConfig:
        """Get configuration for specific subreddit."""
        for subreddit in self.config.subreddits:
            if subreddit.name == subreddit_name:
                return subreddit
        raise ValueError(f"No configuration found for subreddit: {subreddit_name}")

    def reload_config(self):
        """Reload configuration from file."""
        self.load_config()
```

---

## 🧪 Phase 4: Testing & Documentation (Week 5)

### Step 4.1: Create Unit Tests

**File**: `tests\unit\test_content_checker.py`

```python
"""Unit tests for ContentChecker."""
import unittest
from unittest.mock import Mock, patch
from bot.core.content_checker import ContentChecker


class TestContentChecker(unittest.TestCase):
    """Test cases for ContentChecker class."""

    def setUp(self):
        """Set up test fixtures."""
        with patch('bot.core.content_checker.conf') as mock_conf:
            mock_conf.return_value.get.side_effect = lambda key: {
                'bot_name': 'testbot',
                'bot_account': ['testbot'],
                'blocked_account': ['blockeduser'],
                'blacklist': ['blacklisteduser']
            }.get(key, [])
            self.checker = ContentChecker()

    def test_check_status_normal(self):
        """Test check_status with normal content."""
        mock_content = Mock()
        mock_content.selftext = "Normal content"

        result = self.checker.check_status(mock_content)
        self.assertEqual(result, "normal")

    def test_check_status_removed(self):
        """Test check_status with removed content."""
        mock_content = Mock()
        mock_content.selftext = "[removed]"

        result = self.checker.check_status(mock_content)
        self.assertEqual(result, "removed")

    def test_check_at_me_mentioned(self):
        """Test check_at_me when bot is mentioned."""
        mock_content = Mock()
        mock_content.selftext = "Hey u/testbot, what do you think?"
        mock_content.author = "someuser"

        result = self.checker.check_at_me(mock_content, "testbot")
        self.assertTrue(result)

    def test_check_at_me_not_mentioned(self):
        """Test check_at_me when bot is not mentioned."""
        mock_content = Mock()
        mock_content.selftext = "Just a regular post"
        mock_content.author = "someuser"

        result = self.checker.check_at_me(mock_content, "testbot")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
```

**File**: `tests\unit\test_ai_providers.py`

```python
"""Unit tests for AI providers."""
import unittest
from unittest.mock import Mock, patch
from ai.factory import AIProviderFactory


class TestAIProviderFactory(unittest.TestCase):
    """Test cases for AI provider factory."""

    def test_create_azure_provider(self):
        """Test creating Azure provider."""
        with patch('ai.providers.azure.azure_generate_reply'):
            provider = AIProviderFactory.create_provider('AZURE')
            self.assertIsNotNone(provider)

    def test_unsupported_provider(self):
        """Test creating unsupported provider raises error."""
        with self.assertRaises(ValueError):
            AIProviderFactory.create_provider('UNSUPPORTED')

    def test_get_available_providers(self):
        """Test getting list of available providers."""
        providers = AIProviderFactory.get_available_providers()
        self.assertIn('AZURE', providers)
        self.assertIn('GEMINI', providers)


if __name__ == '__main__':
    unittest.main()
```

### Step 4.2: Create Integration Tests

**File**: `tests\integration\test_reddit_integration.py`

```python
"""Integration tests for Reddit functionality."""
import unittest
from unittest.mock import Mock, patch
from bot.core.reddit_client import RedditClient


class TestRedditIntegration(unittest.TestCase):
    """Integration tests for Reddit client."""

    @patch('bot.core.reddit_client.praw.Reddit')
    @patch('bot.core.reddit_client.conf')
    def test_reddit_client_initialization(self, mock_conf, mock_reddit):
        """Test Reddit client initializes correctly."""
        # Mock configuration
        mock_conf.return_value.get.side_effect = lambda key: {
            'bot_name': 'testbot',
            'password': 'testpass',
            'client_id': 'testid',
            'client_secret': 'testsecret',
            'TargetSubreddits': [{'test': {}}]
        }.get(key, [])

        # Mock Reddit instance
        mock_reddit_instance = Mock()
        mock_reddit.return_value = mock_reddit_instance

        client = RedditClient()

        self.assertIsNotNone(client.reddit)
        mock_reddit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
```

### Step 4.3: Create Test Fixtures

**File**: `tests\fixtures\sample_posts.json`

```json
{
  "submissions": [
    {
      "id": "test123",
      "title": "Test submission",
      "selftext": "This is a test submission",
      "author": "testuser",
      "url": "https://reddit.com/r/test/comments/test123"
    }
  ],
  "comments": [
    {
      "id": "comment456",
      "body": "This is a test comment",
      "author": "testuser",
      "link_id": "t3_test123"
    }
  ]
}
```

### Step 4.4: Create Documentation

**File**: `docs\setup.md`

````markdown
# Reddit Bot Setup Guide

## Prerequisites

- Python 3.8+
- Reddit API credentials
- AI provider credentials (Azure/Gemini/Cohere/DeepSeek)

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `config-template.json` to `config.json`
4. Fill in your credentials in `config.json`

## Configuration

See `configuration.md` for detailed configuration options.

## Running the Bot

```bash
python app.py
```
````

## Testing

```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests
python -m pytest tests/integration/

# Run all tests
python -m pytest tests/
```

````

**File**: `docs\configuration.md`

```markdown
# Configuration Guide

## Main Configuration File

The bot uses `config.json` for all configuration. Here's the structure:

### Reddit Configuration
- `bot_name`: Your bot's Reddit username
- `password`: Bot account password
- `client_id`: Reddit API client ID
- `client_secret`: Reddit API client secret

### AI Configuration
- `ai_model`: AI provider to use (AZURE/GEMINI/COHERE/DEEPSEEK)
- `ai_temperature`: Response creativity (0.0-1.0)
- `max_retries`: Max retry attempts for failed requests

### Subreddit Configuration
Each subreddit needs:
- `bot_callname`: How the bot is mentioned
- `bot_nickname`: Bot's display name
- `sub_user_nickname`: How to address users
- `persona_file`: Path to persona file

## Environment Variables

You can enable new features gradually:
- `USE_NEW_CONTENT_CHECKER=true`: Enable new content checking
- `USE_NEW_REDDIT_CLIENT=true`: Enable new Reddit client
````

---

## 🚀 Migration Timeline

### Week 1: Foundation

- [ ] Create directory structure
- [ ] Extract utility functions
- [ ] Create Reddit client wrapper
- [ ] Add compatibility layer

### Week 2: Core Logic

- [ ] Extract content checker
- [ ] Create reply generator base
- [ ] Add unit tests for utilities
- [ ] Test compatibility layer

### Week 3: AI Integration

- [ ] Create AI provider abstractions
- [ ] Implement all AI providers
- [ ] Create provider factory
- [ ] Test AI provider switching

### Week 4: Configuration

- [ ] Create configuration classes
- [ ] Add configuration validation
- [ ] Create configuration manager
- [ ] Test configuration loading

### Week 5: Testing & Documentation

- [ ] Complete unit test suite
- [ ] Add integration tests
- [ ] Write documentation
- [ ] Performance testing

---

## 🛡️ Risk Mitigation

### Rollback Strategy

1. Keep original `AIbot_utils.py` as backup
2. Use feature flags for gradual migration
3. Test each phase in isolation
4. Monitor bot performance throughout migration

### Testing Strategy

1. Unit tests for each new module
2. Integration tests for Reddit API
3. End-to-end tests for full workflow
4. Performance regression tests

### Monitoring

1. Add logging to new modules
2. Monitor response times
3. Track error rates
4. Alert on configuration issues

---

## 📝 Post-Migration Benefits

1. **Maintainability**: Clear separation of concerns
2. **Testability**: Comprehensive test coverage
3. **Scalability**: Easy to add new features
4. **Reliability**: Better error handling and validation
5. **Performance**: Optimized AI provider switching
6. **Documentation**: Clear setup and usage guides

---

## ✅ Completion Checklist

- [ ] All utility functions extracted
- [ ] Content checker modularized
- [ ] AI providers abstracted
- [ ] Configuration validated
- [ ] Tests passing (>90% coverage)
- [ ] Documentation complete
- [ ] Performance benchmarked
- [ ] Original functionality preserved
- [ ] Feature flags removed
- [ ] Code review completed

Follow this plan step by step, testing each phase thoroughly before proceeding to the next. The gradual migration approach ensures your bot continues working throughout the restructuring process.
