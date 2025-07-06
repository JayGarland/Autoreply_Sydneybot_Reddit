"""
Configuration constants for context building.
Extracted from magic numbers scattered throughout the codebase.
"""

class ContextConfig:
    """Configuration constants for context building"""
    
    # Content limits
    MAX_ANCESTOR_DEPTH = 30
    TOP_COMMENTS_LIMIT = 3
    MAX_SUBMISSION_CONTENT_LENGTH = 6000
    MAX_COMMENT_LENGTH = 300
    MAX_POST_CONTENT_LENGTH = 500
    MAX_CONTEXT_LENGTH = 1000
    
    # User history limits
    USER_HISTORY_POST_LIMIT = 5
    USER_HISTORY_COMMENT_LIMIT = 10
    
    # API and performance limits
    BATCH_SIZE = 50
    MAX_MENTIONS_TO_FIND = 3
    
    # Context section identifiers
    SUBREDDIT_CONTEXT_ID = "subreddit_context"
    CONVERSATION_CONTEXT_ID = "conversation_context"
    USER_HISTORY_ID = "user_history"
    USER_PORTRAIT_ID = "user_portrait"
    REPLY_STRATEGY_ID = "reply_strategy"
    ADDITIONAL_INSTRUCTIONS_ID = "additional_instructions"


class PromptConfig:
    """Configuration for prompt templates and user analysis"""
    
    # User portrait analysis categories
    USER_PORTRAIT_CATEGORIES = {
        "personal_traits": "个人特征推测",
        "communication_preferences": "交流偏好",
        "current_state": "当前状态判断",
        "real_life_speculation": "现实生活推测"
    }
    
    # Personal traits subcategories
    PERSONAL_TRAITS = [
        "年龄段：[基于话题、表达方式、技术熟悉度推断]",
        "职业背景：[从专业知识、发帖时间、讨论话题推断]",
        "教育水平：[从语言复杂度、逻辑思维、知识面判断]",
        "性格特点：[从互动方式、情绪表达、争论风格分析]"
    ]
    
    # Communication preferences subcategories  
    COMMUNICATION_PREFERENCES = [
        "信息接收方式：[详细解释 vs 简洁要点]",
        "社交风格：[正式 vs 随意，严肃 vs 幽默]",
        "学习模式：[提问型 vs 自研型，理论 vs 实践]",
        "决策方式：[理性分析 vs 直觉判断]"
    ]
    
    # Current state subcategories
    CURRENT_STATE = [
        "情绪状态：[从最近发言语调判断]",
        "知识需求：[当前遇到的问题类型]",
        "参与动机：[寻求帮助 vs 分享知识 vs 娱乐]"
    ]
    
    # Real life speculation subcategories
    REAL_LIFE_SPECULATION = [
        "生活状态：[学生/职场人士/退休等]",
        "兴趣爱好：[从参与的社区和话题推断]",
        "社交圈子：[技术圈/游戏圈/学术圈等]",
        "个人挑战：[当前可能面临的问题或困扰]"
    ]
    
    # Personalization strategies
    PERSONALIZATION_STRATEGIES = [
        "语言风格和专业深度 - 根据用户知识水平调整解释详细程度",
        "信息组织方式和举例类型 - 匹配用户的学习偏好",
        "互动语调和情感表达 - 适应用户当前情绪和社交风格",
        "内容重点和价值导向 - 基于用户兴趣突出相关方面",
        "现实关怀 - 如果合适，可以结合用户可能的现实处境给予建议"
    ]
    
    # Instructions for different context types
    SUBMISSION_INSTRUCTIONS = (
        "请在内心默默分析用户画像，但不要在回复中展示分析过程或结果。"
        "直接基于分析结果个性化回复即可。回复时不要重复或仿写你打算回复的{sub_user_nickname}说过的话。"
        "不必介绍你自己，只输出你回复内容的正文。不要附上原文，不要输出所有可能的回复。"
        "不要输出用户画像分析内容。"
    )
    
    COMMENT_INSTRUCTIONS = (
        "请在内心默默分析用户画像，想象这个人在现实生活中的样子，但不要在回复中展示分析过程或结果。"
        "直接基于分析结果个性化回复即可。回复时不要重复或仿写你打算回复的{sub_user_nickname}说过的话。"
        "不必介绍你自己，只输出你回复的内容正文。不要附上原文，不要输出所有可能的回复。"
        "后续要求回复时，不要回复帖子本身，要回复{sub_user_nickname} {comment_author} 的最后一条评论:{comment_body}。"
        "不要输出用户画像分析内容。"
    )
