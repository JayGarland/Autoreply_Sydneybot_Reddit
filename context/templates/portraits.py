"""
User portrait generation templates.
Handles creation of detailed user analysis prompts.
"""

from ..config import PromptConfig


class UserPortraitTemplate:
    """Template for user portrait analysis instructions"""
    
    def __init__(self):
        self.config = PromptConfig()
    
    def generate_analysis_prompt(self, sub_user_nickname, include_real_life=False):
        """
        Generate detailed user portrait analysis prompt.
        
        Args:
            sub_user_nickname: Nickname for users in this subreddit
            include_real_life: Whether to include real life speculation section
            
        Returns:
            str: Formatted portrait analysis prompt
        """
        prompt = f"请基于以上历史数据，构建此{sub_user_nickname}的详细画像：\n\n"
        
        # Personal traits section
        prompt += f"{self.config.USER_PORTRAIT_CATEGORIES['personal_traits']}：\n"
        for trait in self.config.PERSONAL_TRAITS:
            prompt += f"- {trait}\n"
        prompt += "\n"
        
        # Communication preferences section
        prompt += f"{self.config.USER_PORTRAIT_CATEGORIES['communication_preferences']}：\n"
        for pref in self.config.COMMUNICATION_PREFERENCES:
            prompt += f"- {pref}\n"
        prompt += "\n"
        
        # Current state section
        prompt += f"{self.config.USER_PORTRAIT_CATEGORIES['current_state']}：\n"
        for state in self.config.CURRENT_STATE:
            prompt += f"- {state}\n"
        prompt += "\n"
        
        # Real life speculation (only for comments, not submissions)
        if include_real_life:
            prompt += f"{self.config.USER_PORTRAIT_CATEGORIES['real_life_speculation']}：\n"
            for speculation in self.config.REAL_LIFE_SPECULATION:
                prompt += f"- {speculation}\n"
            prompt += "\n"
        
        return prompt.rstrip()
    
    def generate_strategy_prompt(self, include_real_care=False):
        """
        Generate personalization strategy prompt.
        
        Args:
            include_real_care: Whether to include real life care strategy
            
        Returns:
            str: Formatted strategy prompt
        """
        prompt = "个性化回复策略：\n"
        prompt += "基于用户画像，请采用最适合此用户的：\n"
        
        strategies = self.config.PERSONALIZATION_STRATEGIES.copy()
        if not include_real_care:
            # Remove real care strategy for submissions
            strategies = strategies[:-1]
        
        for i, strategy in enumerate(strategies, 1):
            prompt += f"{i}. {strategy}\n"
        
        return prompt.rstrip() + "\n"
