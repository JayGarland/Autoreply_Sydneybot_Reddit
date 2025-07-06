"""
Base template system for context building.
Provides modular, reusable templates for different context sections.
"""

from ..config import ContextConfig


class ContextTemplate:
    """Base template system for context sections"""
    
    # Section templates with consistent formatting
    SUBREDDIT_SECTION = "[system](#{section_id})\n{content}\n\n"
    USER_HISTORY_SECTION = "[system](#{section_id})\n{content}\n\n"
    USER_PORTRAIT_SECTION = "[system](#{section_id})\n{content}\n\n"
    REPLY_STRATEGY_SECTION = "[system](#{section_id})\n{content}\n\n"
    ADDITIONAL_INSTRUCTIONS_SECTION = "[system](#{section_id})\n{content}"
    
    @classmethod
    def format_section(cls, template, section_id, content):
        """Format a template section with content"""
        return template.format(section_id=section_id, content=content)
    
    @classmethod
    def subreddit_context(cls, content):
        """Format subreddit context section"""
        return cls.format_section(
            cls.SUBREDDIT_SECTION, 
            ContextConfig.SUBREDDIT_CONTEXT_ID, 
            content
        )
    
    @classmethod
    def conversation_context(cls, content):
        """Format conversation context section"""
        return cls.format_section(
            cls.SUBREDDIT_SECTION,  # Using same template
            ContextConfig.CONVERSATION_CONTEXT_ID,
            content
        )
    
    @classmethod
    def user_history(cls, content):
        """Format user history section"""
        return cls.format_section(
            cls.USER_HISTORY_SECTION,
            ContextConfig.USER_HISTORY_ID,
            content
        )
    
    @classmethod
    def user_portrait(cls, content):
        """Format user portrait section"""
        return cls.format_section(
            cls.USER_PORTRAIT_SECTION,
            ContextConfig.USER_PORTRAIT_ID,
            content
        )
    
    @classmethod
    def reply_strategy(cls, content):
        """Format reply strategy section"""
        return cls.format_section(
            cls.REPLY_STRATEGY_SECTION,
            ContextConfig.REPLY_STRATEGY_ID,
            content
        )
    
    @classmethod
    def additional_instructions(cls, content):
        """Format additional instructions section"""
        return cls.format_section(
            cls.ADDITIONAL_INSTRUCTIONS_SECTION,
            ContextConfig.ADDITIONAL_INSTRUCTIONS_ID,
            content
        )
