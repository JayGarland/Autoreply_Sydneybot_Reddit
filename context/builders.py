"""
Main context builder orchestrator.
Coordinates all providers to build complete context strings.
"""

from .providers.subreddit import SubredditContextProvider
from .providers.conversation import ConversationContextProvider
from .providers.user_analyzer import UserAnalyzer
from .templates.base import ContextTemplate
from .templates.portraits import UserPortraitTemplate
from .config import PromptConfig


class ContextBuilder:
    """Main orchestrator for context building"""
    
    def __init__(self, reddit_client):
        """
        Initialize the context builder with all providers.
        
        Args:
            reddit_client: Reddit API client instance
        """
        self.reddit = reddit_client
        
        # Initialize providers
        self.subreddit_provider = SubredditContextProvider()
        self.conversation_provider = ConversationContextProvider(reddit_client)
        self.user_analyzer = UserAnalyzer(reddit_client)
        
        # Initialize templates
        self.template = ContextTemplate()
        self.portrait_template = UserPortraitTemplate()
        self.prompt_config = PromptConfig()
    
    def build_submission_context(self, submission, sub_user_nickname):
        """
        Build complete context for submission replies.
        
        Args:
            submission: Reddit submission object
            sub_user_nickname: User nickname for this subreddit
            
        Returns:
            str: Complete formatted context string
            
        TODO: Add conversation continuity - track previous bot interactions with same user
        TODO: Add advanced persona adjustment based on user type detection
        TODO: Add analytics tracking for personalized response effectiveness
        TODO: Add multi-language adaptation - detect user's primary language, cultural context awareness
        TODO: Add dynamic persona modification based on user characteristics in real-time
        """
        context_parts = []
        
        # 1. Subreddit context
        subreddit_content = self.subreddit_provider.get_subreddit_context(submission.subreddit)
        context_parts.append(self.template.subreddit_context(subreddit_content))
        
        # 2. Conversation context (submission details)
        conversation_content = self.subreddit_provider.get_submission_overview(submission)
        context_parts.append(self.template.conversation_context(conversation_content))
        
        # 3. User history analysis
        user_history = self.user_analyzer.get_user_history(str(submission.author), sub_user_nickname)
        if user_history:
            # Add user history section
            history_content = f"以下是{submission.author}的近期发帖和评论历史：\n\n{user_history}"
            context_parts.append(self.template.user_history(history_content))
            
            # Add user portrait generation instructions
            portrait_content = self.portrait_template.generate_analysis_prompt(
                sub_user_nickname, include_real_life=False  # No real life speculation for submissions
            )
            context_parts.append(self.template.user_portrait(portrait_content))
        
        # 4. Reply strategy
        strategy_content = self.portrait_template.generate_strategy_prompt(include_real_care=False)
        context_parts.append(self.template.reply_strategy(strategy_content))
        
        # 5. Additional instructions
        instructions = self.prompt_config.SUBMISSION_INSTRUCTIONS.format(
            sub_user_nickname=sub_user_nickname
        )
        context_parts.append(self.template.additional_instructions(instructions))
        
        return "".join(context_parts)
    
    def build_comment_context(self, comment, ancestors, sub_user_nickname, 
                            bot_nickname, bot_name, bot_name_list):
        """
        Build complete context for comment replies.
        
        Args:
            comment: The comment being replied to
            ancestors: List of ancestor comments
            sub_user_nickname: User nickname for this subreddit
            bot_nickname: Bot's nickname
            bot_name: Bot's username  
            bot_name_list: List of bot usernames
            
        Returns:
            str: Complete formatted context string
            
        TODO: Add conversation continuity tracking for this specific user
        TODO: Add advanced persona adjustment based on detected user characteristics  
        TODO: Add multi-language detection and adaptation
        TODO: Add analytics tracking for response quality and user engagement
        TODO: Add performance analytics - API usage efficiency, response time impact monitoring
        TODO: Add quality control - detect inappropriate personalization, prevent stalking-like behavior
        """
        context_parts = []
        
        # Get submission for subreddit context
        submission = self.reddit.submission(comment.link_id[3:])
        
        # 1. Subreddit context  
        subreddit_content = self.subreddit_provider.get_subreddit_context(submission.subreddit)
        context_parts.append(self.template.subreddit_context(subreddit_content))
        
        # 2. Conversation context (thread)
        conversation_content = self.conversation_provider.get_conversation_thread(
            comment, ancestors, sub_user_nickname, bot_nickname, bot_name, bot_name_list
        )
        context_parts.append(self.template.conversation_context(conversation_content))
        
        # 3. Related comments
        related_comments = self.conversation_provider.get_related_comments(
            submission, sub_user_nickname, bot_name_list
        )
        context_parts.append(related_comments)  # Already formatted
        
        # 4. User history analysis  
        comment_author = str(ancestors[0].author)  # Get original comment author
        user_history = self.user_analyzer.get_user_history(comment_author, sub_user_nickname)
        if user_history:
            # Add user history section
            history_content = f"以下是{comment_author}的近期发帖和评论历史：\n\n{user_history}"
            context_parts.append(self.template.user_history(history_content))
            
            # Add user portrait generation instructions (with real life speculation for comments)
            portrait_content = self.portrait_template.generate_analysis_prompt(
                sub_user_nickname, include_real_life=True
            )
            context_parts.append(self.template.user_portrait(portrait_content))
        
        # 5. Reply strategy
        strategy_content = self.portrait_template.generate_strategy_prompt(include_real_care=True)
        context_parts.append(self.template.reply_strategy(strategy_content))
        
        # 6. Additional instructions
        instructions = self.prompt_config.COMMENT_INSTRUCTIONS.format(
            sub_user_nickname=sub_user_nickname,
            comment_author=ancestors[0].author,
            comment_body=ancestors[0].body
        )
        context_parts.append(self.template.additional_instructions(instructions))
        
        return "".join(context_parts)
    
    def build_subreddit_context(self, submission_list, sub_user_nickname, subreddit_name):
        """
        Build subreddit context from a list of submissions.
        
        Args:
            submission_list: List of Reddit submission objects
            sub_user_nickname: User nickname for this subreddit
            subreddit_name: Name of the subreddit
            
        Returns:
            str: Formatted subreddit context string
        """
        return self.subreddit_provider.get_submission_list_context(
            submission_list, sub_user_nickname, subreddit_name
        )
