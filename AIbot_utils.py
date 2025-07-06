#TODO: when reply review also the user's history of posts and comments so that the bot can reply more accurately to the person's comment
import praw
import pickle
import os
import random
import bleach
import re
from log import logger
from config import load_config, conf
import requests
from io import BytesIO
from PIL import Image
from praw.exceptions import ClientException

# Import new modular context builder
from context.builders import ContextBuilder
from context.builders import ContextBuilder


# load_config()
bot_name = conf().get('bot_name')  # bot account
password = conf().get('password') # bot pswd
client_id = conf().get('client_id') # api id
client_secret = conf().get('client_secret')  # api 密钥

user_agent = "autoreply bot created by u/Chinese_Dictator."  # 这一项可以随意填写
targetSubreddits = conf().get('TargetSubreddits')
subreddit_names =  [list(targetSubreddits[i].keys())[0] for i in range(len(targetSubreddits))]  # 在哪个 subreddit 运行
# logger.info(subreddit_names)


min_char = conf().get('min_char')  # at least how many word in user's speech will trigger the bot reply
interval = conf().get('interval') # check randomly in every max interval minute
submission_num = conf().get('submission_num')  # everytime bot observe how many posts
comment_num = conf().get('comment_num')  # every pattern when triggered the reply randomly, how many replies will be pulled and let the bot observe
comment_rate = conf().get('comment_rate')  # every pattern when triggered the reply randomly, how much rate of the bot choose to reply the comment under a post, if not, reply to a post
random_check_rate = conf().get('random_check_rate')  # bot everytime when bot checks, how many check patterns would trigger the bot to reply randomly otherwise only reply when someone @ the bot

removed_content_list = ["[removed]", "[deleted]", "[ Removed by Reddit ]"]
blocked_content = "[unavailable]"


reddit = None
subreddit = None
bot_name_list = None
ignore_name_list = None

blacklist = None  # if anyone in the blacklist, the bot will not reply to the whom included whatsoever

bot_statement = conf().get("bot_statement")
ai_model     = conf().get("ai_model")
ignored_content = set()
pickle_path      = "./replied.pkl"
archived_pickle_path = "./replied.pkl.arc"
client = None
i = 1

# Global context builder instance
context_builder = None

def init():
    global reddit
    global subreddit
    global ignored_content
    global context_builder
    global bot_name_list
    global ignore_name_list
    global blacklist
    global random_subReddit

    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, password=password, user_agent=user_agent, username=bot_name)
    random_subReddit = random.choice(subreddit_names)
    subreddit = reddit.subreddit(random_subReddit)

    # Initialize the context builder with the reddit instance
    context_builder = ContextBuilder(reddit)

    bot_name_list = conf().get("bot_account")
    ignore_name_list = conf().get("blocked_account")
    blacklist = conf().get("blacklist")

    if os.path.exists(pickle_path):
        with open(pickle_path, "rb") as pkl:
            ignored_content = pickle.load(pkl)


# 从当前评论开始循环查找上级评论，直至找到主贴
def find_comment_ancestors(comment):
    ancestors = []
    while comment.parent_id.startswith("t1"):
        comment = reddit.comment(comment.parent_id[3:])
        ancestors.append(comment)
        if len(ancestors) > 30:
            break
    return ancestors


# 检查评论、主贴的状态是否正常
def check_status(content) -> str:
    check_str = (content.selftext if (type(content) == praw.models.reddit.submission.Submission) else content.body)
    if check_str in removed_content_list:
        return "removed"
    elif check_str == blocked_content:
        return "blocked"
    else:
        return "normal"


# 检查评论、主贴是否召唤了 bot
def check_at_me(content, bot_nickname) -> bool:
    check_str = (content.selftext if (type(content) == praw.models.reddit.submission.Submission) else content.body)
    # Check if the content author is not the bot name
    if content.author != bot_name:
        if check_str.lower().find(f"u/{bot_name}".lower()) != -1 or re.search(bot_nickname, check_str) is not None:
            return True
        if type(content) == praw.models.reddit.submission.Submission:
            if content.title.lower().find(f"u/{bot_name}".lower()) != -1 or re.search(bot_nickname, content.title) is not None:
                return True
    return False


# 检查评论、主贴是否应当忽略，用于随机触发
def check_ignored(content) -> bool:
    global ignored_content
    if content.id in ignored_content:
        return True
    if content.author in ignore_name_list or content.author in bot_name_list:
        ignored_content.add(content.id)
        return True
    if content.author in blacklist:
        return True
    if content.author == bot_name:
        return True
    if type(content) == praw.models.reddit.submission.Submission:
        content.comments.replace_more(limit=0)
        for comment in content.comments:
            if comment.author in bot_name_list:
                ignored_content.add(content.id)
                return True
    else:
        content.refresh()
        for reply in content.replies:
            if reply.author in bot_name_list:
                ignored_content.add(content.id)
                return True
    return False


# 检查评论、主贴是否已回复过，用于召唤触发
def check_replied(content) -> bool:
    global ignored_content
    if content.id in ignored_content:
        return True
    if content.author in bot_name_list:
        ignored_content.add(content.id)
        return True
    if content.author in blacklist:
        return True
    if type(content) == praw.models.reddit.submission.Submission:
        content.comments.replace_more(limit=0)
        for comment in content.comments:
            if comment.author == bot_name:
                ignored_content.add(content.id)
                return True
    else:
        # try to refresh replies; if missing, treat as already handled
        try:
            content.refresh()
        except ClientException as e:
            logger.warning(f"Could not refresh comment {content.id}: {e} -- marking as replied")
            ignored_content.add(content.id)
            return True

        for reply in content.replies:
            if reply.author == bot_name:
                ignored_content.add(content.id)
                return True
    return False


# 将当前 sub 中所有主贴的标题和内容拼接成一个字符串
def submission_list_to_context(submission_list, sub_user_nickname, subreddit):
    """Use modular context builder for subreddit context (legacy wrapper)"""
    return context_builder.build_subreddit_context(
        submission_list=submission_list,
        sub_user_nickname=sub_user_nickname,
        subreddit_name=subreddit.display_name
    )

def get_user_history(username, post_limit=5, comment_limit=10, sub_user_nickname="用户"):
    """Legacy wrapper - now handled by UserAnalyzer in context builder"""
    # This function is deprecated but kept for compatibility
    # The actual user history fetching is now done in context_builder.user_analyzer
    return ""  # Return empty string for backward compatibility

def build_submission_context(submission, sub_user_nickname):
    """
    Build context for submission replies using the new modular context builder.
    This replaces the legacy monolithic implementation.
    """
    return context_builder.build_submission_context(submission, sub_user_nickname)

# 删除 bot 回复末尾声明自己是 bot 的话
def remove_bot_statement(reply: str) -> str:
    return "\n\n".join(reply.strip().split("\n\n")[:-1]).strip()


# 删除多余的回复格式
def remove_extra_format(reply: str) -> str:
    pattern = r'回复[^：]*：(.*)'
    result = re.search(pattern, reply, re.S)
    if result is None:
        return reply
    result = result.group(1).strip()
    if result.startswith("“") and result.endswith("”"):
        result = result[1:-1]
    return result


# 删除回复被中断时回复最末尾未完成的句子
def remove_incomplete_sentence(reply: str) -> str:
    pattern = r"(.*[！!?？。…])"
    result = re.search(pattern, reply, re.S)
    if result is not None:
        return result.group(1).strip()
    else:
        return reply


# 拼接字符串，去除首尾重复部分
def concat_reply(former_str: str, latter_str: str) -> str:
    former_str = former_str.strip()
    latter_str = latter_str.strip()
    min_length = min(len(former_str), len(latter_str))
    for i in range(min_length, 0, -1):
        if former_str[-i:] == latter_str[:i]:
            return former_str + latter_str[i:]
    return former_str + latter_str


def build_comment_context(comment, ancestors, sub_user_nickname, bot_nickname, bot_name):
    """
    Build context for comment replies using the new modular context builder.
    This replaces the legacy monolithic implementation.
    """
    return context_builder.build_comment_context(
        comment=comment,
        ancestors=ancestors,
        sub_user_nickname=sub_user_nickname,
        bot_nickname=bot_nickname,
        bot_name=bot_name,
        bot_name_list=bot_name_list
    )

def traverse_comments(comment_list, method, bot_nickname):
    global ignored_content
    for comment in comment_list:
        if method == "random":
            if "preview.redd.it" in comment.body:
                continue
            if len(comment.body) <= min_char:
                continue
            elif check_replied(comment):
                continue
            elif comment.author == bot_name:
                continue
        if check_status(comment) != "normal":
            continue
        if method == "at_me" and not check_at_me(comment, bot_nickname):
            continue
        if check_at_me(comment, bot_nickname):
            if check_replied(comment):
                continue
        else:
            if check_ignored(comment):
                continue
        belonging_submission = reddit.submission(comment.link_id[3:])
        if check_status(belonging_submission) != "normal":
            ignored_content.add(comment.id)
            continue
        ancestors = find_comment_ancestors(comment)

        # 串中有回复者拉黑了 bot，则无法回复该串
        blocked_thread = False
        for ancestor in ancestors:
            if check_status(ancestor) == "blocked":
                blocked_thread = True
                break
        if blocked_thread:
            ignored_content.add(comment.id)
            continue

        ignored_content.add(comment.id)
        return comment, ancestors
    return None, None


def traverse_submissions(submission_list, method, bot_nickname):
    global ignored_content
    for submission in submission_list:
        if method == "random":
            if "preview.redd.it" in submission.selftext:
                continue
            if not submission.is_self or (len(submission.title) + len(submission.selftext)) <= min_char:
                continue
            elif check_replied(submission):
                continue
        if check_status(submission) != "normal":
            continue
        if method == "at_me" and not check_at_me(submission, bot_nickname):
            continue
        if check_at_me(submission, bot_nickname):
            if check_replied(submission):
                continue
        else:
            if check_ignored(submission):
                continue
        ignored_content.add(submission.id)
        return submission
    return None

def detect_chinese_char_pair(context, threshold=5):
    # create a dictionary to store the frequency of each pair of consecutive chinese characters
    freq = {}
    # loop through the context with a sliding window of size 2
    for i in range(len(context) - 1):
        # get the current pair of characters
        pair = context[i:i+2]
        # check if both characters are chinese characters using the unicode range
        if '\u4e00' <= pair[0] <= '\u9fff' and '\u4e00' <= pair[1] <= '\u9fff':
            # increment the frequency of the pair or set it to 1 if not seen before
            freq[pair] = freq.get(pair, 0) + 1
    # loop through the frequency dictionary
    for pair, count in freq.items():
        # check if the count is greater than or equal to the threshold
        if count >= threshold:
            # return True and the pair
            return True, pair
    # return False and None if no pair meets the threshold
    return False, None

def init_systemprompt_bot(sub_user_nickname, bot_nickname):
    persona = None
    for setting_pairs in conf().get("customSet"):  # customSet is now a list of dicts with file paths
        for key, cusprompt in dict(setting_pairs).items():
            if key == subreddit:
                # If cusprompt is a file path and exists, read the file
                if isinstance(cusprompt, str) and os.path.isfile(cusprompt):
                    with open(cusprompt, 'r', encoding='utf-8') as f:
                        persona = f.read()
                else:
                    persona = cusprompt
                break
    if not persona:
        # persona = conf().get("persona")
        # throw exception if no persona is found
        raise ValueError(f"No persona found for subreddit {subreddit}. Please check your configuration.")
    try:
        persona = persona.format(n=sub_user_nickname, k=bot_nickname, m=subreddit)
    except ValueError as e:
        logger.warning(str(e))
        # Escape all single braces to avoid format errors
        persona = persona.replace('{', '{{').replace('}', '}}')
        persona = persona.format(n=sub_user_nickname, k=bot_nickname, m=subreddit)
    logger.debug("PERSONA:" + persona)
    return persona

def askbyuser(ask_string):
    res = []
    res.append({
            "role": "user",
            "parts": [{"text": ask_string}]
        })
    return res

def get_image_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

def generate_reply(content, context, sub_user_nickname, bot_statement, bot_nickname, retry_count=0):
    """Generate and post a reply using the configured LLM client."""
    MAX_RETRIES = 3
    if retry_count > MAX_RETRIES:
        logger.error(f"Failed after maximum retry attempts ({MAX_RETRIES})")
        return

    # prepend system tag and clean
    context = "<|im_start|>system\n\n" + bleach.clean(context).strip()

    # build ask prompt and optional image URL
    is_sub = isinstance(content, praw.models.reddit.submission.Submission)
    if is_sub:
        ask = f"{bot_nickname}请回复前述{content.author}的帖子。"
        img_url = content.url if getattr(content, "url", "").lower().endswith((".jpg", ".png", ".jpeg", ".gif")) else None
    else:
        ask = (
            f"{bot_nickname}请回复"
            " 不必介绍你自己，只输出你回复内容的正文。不要排比，不要重复之前回复的内容或格式。"
        )
        img_url = None
        if hasattr(content, "body_html"):
            m = re.search(r'<img src="(.+?)"', content.body_html)
            if m:
                img_url = m.group(1)
        if not img_url and hasattr(content, "submission"):
            sub_url = getattr(content.submission, "url", "")
            if sub_url.lower().endswith((".jpg", ".png", ".jpeg", ".gif")):
                img_url = sub_url

    ask = bleach.clean(ask).strip()
    # logger.info(f"context: {context}")
    # logger.info(f"ask: {ask}")
    logger.info(f"image: {img_url or 'None'}")

    try:
        persona = init_systemprompt_bot(sub_user_nickname, bot_nickname)
        messages = [{"role": "SYSTEM", "content": context}]
        query = ask if not img_url else [ask, get_image_from_url(img_url)]

        if ai_model == 'COHERE':
            resp = client.chat(message=query, preamble=persona, chat_history=messages, temperature=0.7)
            reply = resp.text
        elif ai_model == 'DEEPSEEK':
            msgs = [
                {"role": "system", "content": persona + context},
                {"role": "user",   "content": ask}
            ]
            comp = client.chat.completions.create(
                model="deepseek-reasoner",
                messages=msgs,
                temperature=0.7
            )
            reply = re.sub(r'<think>.*?</think>', '', comp.choices[0].message.content, flags=re.DOTALL).strip()
        elif ai_model == 'GEMINI':
            model = client.GenerativeModel("gemini-pro")
            convo = model.start_chat(history=[])
            reply = convo.send_message(persona + "\n" + context + "\n" + ask).text
        elif ai_model == 'AZURE':
            azure_reply(content, context, sub_user_nickname, bot_statement, bot_nickname, retry_count)
            return
        else:
            raise ValueError(f"Unsupported AI model: {ai_model}")

        # ensure bot_statement is appended
        if bot_statement.strip() not in reply:
            reply = reply.rstrip() + "\n\n" + bot_statement

        content.reply(reply)

    except Exception as e:
        logger.warning(f"generate_reply error ({retry_count + 1}/{MAX_RETRIES}): {e}")
        generate_reply(content, context, sub_user_nickname, bot_statement, bot_nickname, retry_count + 1)

# (no alias needed)
def azure_reply(content, context, sub_user_nickname, bot_statement, bot_nickname, retry_count = 0):
    """
    Generate a reply using Azure AI Inference and post to Reddit.
    """
    from azure_inference import azure_generate_reply
    if retry_count > 3:
        logger.error("Failed after maximum number of retry times (Azure)")
        return
    context = bleach.clean(context).strip()
    if type(content) == praw.models.reddit.submission.Submission:
        ask_string = f"{bot_nickname}请回复前述{content.author}的帖子。"
    else:
        ask_string = f"{bot_nickname}请回复。不必介绍你自己，只输出你回复的内容正文。不要排比，不要重复之前回复的内容或格式。"
    ask_string = bleach.clean(ask_string).strip()
    logger.info(f"[AZURE] context: {context}")
    logger.info(f"[AZURE] ask_string: {ask_string}")
    try:
        persona = init_systemprompt_bot(sub_user_nickname, bot_nickname)
        system_prompt = persona + context
        user_prompt = ask_string
        reply_text = azure_generate_reply(system_prompt, user_prompt)
        logger.info(reply_text)
        if "要和我对话请在发言中带上" not in reply_text:
            reply_text += bot_statement
        content.reply(reply_text)
        return
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.warning(e)
        azure_reply(content, context, sub_user_nickname, bot_statement, bot_nickname, retry_count + 1)

def fetch_comments_efficiently(subreddit, method, target_count, bot_nickname):
    """
    Smart comment fetching that stops early when enough mentions found.
    TODO: Add pagination support for large subreddits
    TODO: Add caching for recent comment fetches
    TODO: Add rate limiting per subreddit
    """
    if method == "random":
        # For random mode, fetch exact target count
        comment_list = list(subreddit.comments(limit=target_count))
        random.shuffle(comment_list)
        return comment_list
    
    elif method == "at_me":
        # For mention detection, fetch in batches and stop early when found
        batch_size = min(target_count, 50)  # Fetch in smaller batches
        max_total = target_count * 10  # Maximum to fetch (same as before)
        comments_found = []
        mentions_found = 0
        total_fetched = 0
        
        try:
            for comment in subreddit.comments(limit=max_total):
                comments_found.append(comment)
                total_fetched += 1
                
                # Check if this comment mentions the bot
                if check_at_me(comment, bot_nickname):
                    mentions_found += 1
                
                # Stop early if we found enough mentions or reached batch limit
                if mentions_found >= 3 or total_fetched >= batch_size:
                    logger.debug(f"Early stop: found {mentions_found} mentions in {total_fetched} comments")
                    break
                    
                # If no mentions found in first batch, continue but limit total
                if total_fetched >= max_total:
                    break
                    
        except Exception as e:
            logger.warning(f"Error fetching comments efficiently: {e}")
            # Fallback to simple fetch
            comments_found = list(subreddit.comments(limit=target_count))
        
        random.shuffle(comments_found)
        return comments_found
    
    else:
        # Fallback for unknown methods
        comment_list = list(subreddit.comments(limit=target_count))
        random.shuffle(comment_list)
        return comment_list

def task():
    global i
    init()
    logger.info(subreddit)

    for reddit in conf().get("TargetSubreddits"):
        if random_subReddit in reddit:
            bot_callname = r'{}'.format(reddit[random_subReddit]["bot_callname"])
            bot_nickname = reddit[random_subReddit]["bot_nickname"]
            sub_user_nickname = reddit[random_subReddit]["sub_user_nickname"]
            break

    if random_check_rate == 0:
        method = "at_me"
    elif i % random_check_rate == 0:
        method = "random"
    else:
        method = "at_me"
    submission_list = list(subreddit.new(limit=submission_num))
    random.shuffle(submission_list)
    
    # Use smart comment fetching instead of wasteful approach
    comment_list = fetch_comments_efficiently(subreddit, method, comment_num, bot_callname)
    comment = None
    context_str = submission_list_to_context(submission_list, sub_user_nickname, subreddit)
    if method == "at_me" or random.random() < comment_rate:
        comment, ancestors = traverse_comments(comment_list=comment_list, method=method, bot_nickname=bot_callname)
        if comment is not None:
            context_str += build_comment_context(comment, ancestors, sub_user_nickname, bot_nickname, bot_name)
            generate_reply(comment, context_str, sub_user_nickname, bot_statement.format(k=bot_nickname), bot_nickname)
    if comment is None:
        submission = traverse_submissions(submission_list=submission_list, method=method, bot_nickname=bot_callname)
        if submission is not None:
            context_str += build_submission_context(submission, sub_user_nickname)
            generate_reply(submission, context_str, sub_user_nickname, bot_statement.format(k=bot_nickname), bot_nickname)
    logger.info(f"本轮检查结束，方法是 {method}。")
    i += 1
