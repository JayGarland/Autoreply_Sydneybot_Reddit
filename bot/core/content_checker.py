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
