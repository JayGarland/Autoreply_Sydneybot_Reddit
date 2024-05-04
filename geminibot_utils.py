import praw
import pickle
import os
import random
import bleach
import re
from log import logger
from config import load_config, conf
import google.generativeai as genai
from google.generativeai.types.safety_types import HarmCategory, HarmBlockThreshold
import random

load_config()
bot_name = conf().get('bot_name')  # bot account
password = conf().get('password') # bot pswd
client_id = conf().get('client_id') # api id
client_secret = conf().get('client_secret')  # api keys

user_agent = "autoreply bot created by u/Chinese_Dictator." 
targetSubreddits = conf().get('TargetSubreddits')
subreddit_names =  [list(targetSubreddits[i].keys())[0] for i in range(len(targetSubreddits))]  # 在哪个 subreddit 运行
# logger.info(subreddit_names)


min_char = conf().get('min_char')  # at least how many word in user's speech will trigger the bot reply
interval = conf().get('interval') # check every interval minute
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
ignored_content = set()
pickle_path = "./replied.pkl"
archived_pickle_path = "./replied.pkl.arc"

i = 1

def init():
    global reddit
    global subreddit
    global ignored_content
    global bot_name_list
    global ignore_name_list
    global blacklist
    global random_subReddit
    global SAFETY_SETTINGS

    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, password=password, user_agent=user_agent, username=bot_name)
    random_subReddit = random.choice(subreddit_names)
    subreddit = reddit.subreddit(random_subReddit)

    bot_name_list = conf().get("bot_account")
    ignore_name_list = conf().get("blocked_account")
    blacklist = conf().get("blacklist")

    if os.path.exists(pickle_path):
        with open(pickle_path, "rb") as pkl:
            ignored_content = pickle.load(pkl)

    SAFETY_SETTINGS = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    }


# Loop through parent comments from the current comment until the main post is found 
def find_comment_ancestors(comment):
    ancestors = []
    while comment.parent_id.startswith("t1"):
        comment = reddit.comment(comment.parent_id[3:])
        ancestors.append(comment)
        if len(ancestors) > 30:
            break
    return ancestors


# Check if the status of the comment and main post is normal
def check_status(content) -> str:
    check_str = (content.selftext if (type(content) == praw.models.reddit.submission.Submission) else content.body)
    if check_str in removed_content_list:
        return "removed"
    elif check_str == blocked_content:
        return "blocked"
    else:
        return "normal"


# Check if the comment and main post summoned the bot
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


# Check if the comment and main post should be ignored, for random triggering
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


# Check if the comment and main post have been replied to, for summoning triggering  
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
        content.refresh()
        for reply in content.replies:
            if reply.author == bot_name:
                ignored_content.add(content.id)
                return True
    return False


# Concatenate the titles and contents of all main posts in the current sub into a string
def submission_list_to_context(submission_list, sub_user_nickname, subreddit):
    context_str = f'[system](#context)\nThe current posts in the r/{subreddit} sub are:\n\n'
    for submission in submission_list:
        if check_status(submission) != "normal":
            continue
        submission_str = f"{sub_user_nickname} {submission.author} posted a post titled {submission.title}" 
        if submission.selftext != "":
            # 限制内容长度；Python 切片不会索引越界
            submission_str += f", the content is {submission.selftext[:10000]}"
        submission_str += "\n"
        context_str += submission_str
    return context_str


def build_submission_context(submission, sub_user_nickname):
    context_str = f'[system](#context)\nHere is the post from {sub_user_nickname} {submission.author}.\n'
    context_str += f"The title of the post is {submission.title}"
    if submission.selftext != "":
        # Limit content length; Python slicing will not cause index out of bounds
        context_str += f", the content is {submission.selftext[:10000]}"
    context_str += "\n\n"
    context_str += f"[system][#additional_instructions]\nWhen replying, do not repeat or paraphrase what {sub_user_nickname} said. Do not introduce yourself, only output the body of your reply. Do not include the original text, and do not output all possible replies."
    return context_str


# Remove the statement that the bot is a bot at the end of the bot reply
def remove_bot_statement(reply: str) -> str:
    return "\n\n".join(reply.strip().split("\n\n")[:-1]).strip()


def build_comment_context(comment, ancestors, sub_user_nickname, bot_nickname, bot_name):
    submission = reddit.submission(comment.link_id[3:])
    context_str = f'[system](#context)\nHere is the post from {sub_user_nickname} {submission.author}.\n'
    context_str += f"The title of the post is {submission.title}"
    if submission.selftext != "":
        context_str += f", the content is {submission.selftext}"
    context_str += "\n"
    first_comment = True
    replied_to_author = submission.author
    ancestors.insert(0, comment)
    for ancestor in reversed(ancestors):
        if first_comment:
            first_comment = False
            if ancestor.author in bot_name_list:
                if ancestor.author == bot_name:
                    context_str += f"{bot_nickname} commented on {sub_user_nickname} {replied_to_author}'s post saying {remove_bot_statement(ancestor.body)}\n"  # 评论 -> commented on, 帖子 -> post
                else:
                    context_str += f"{sub_user_nickname} {ancestor.author} commented on {replied_to_author}'s post saying {remove_bot_statement(ancestor.body)}\n"
            elif replied_to_author == bot_name:
                context_str += f"{sub_user_nickname} {ancestor.author} commented on {bot_nickname}'s post saying {ancestor.body}\n"
            else:
                context_str += f"{sub_user_nickname} {ancestor.author} commented on {replied_to_author}'s post saying {ancestor.body}\n"
        else:
            if ancestor.author in bot_name_list:
                if ancestor.author == bot_name:
                    context_str += f"{bot_nickname} replied to {sub_user_nickname} {replied_to_author}'s comment saying {remove_bot_statement(ancestor.body)}\n"  # 评论 -> comment, 回复 -> replied to
                else:
                    context_str += f"{sub_user_nickname} {ancestor.author} replied to {replied_to_author}'s comment saying {remove_bot_statement(ancestor.body)}\n"
            elif replied_to_author == bot_name:
                context_str += f"{sub_user_nickname} {ancestor.author} replied to {bot_nickname}'s comment saying {ancestor.body}\n"
            else:
                context_str += f"{sub_user_nickname} {ancestor.author} replied to {replied_to_author}'s comment saying {ancestor.body}\n"
        replied_to_author = ancestor.author

    context_str += "\n\n"
    context_str += f"Here are some other comments from {sub_user_nickname} under this post:\n"  # 在此帖子下 -> under this post
    submission.comment_sort= "top"
    top_comments = submission.comments.list()[:3]
    for comment in top_comments:
        if comment.author not in bot_name_list:
            context_str += comment.body + "(" + str(comment.score) + " upvotes)" + "\n"  # 点赞 -> upvotes

    context_str += "\n\n"
    context_str += f"[system][#additional_instructions]\nWhen replying, do not repeat or paraphrase what the {sub_user_nickname} you are replying to has said. Do not introduce yourself, only output the main text of your reply. Do not attach the original text, and do not output all possible replies. Do not reply to the post itself, but to the last comment of {sub_user_nickname} {ancestor.author}: {ancestor.body}."
    return context_str


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

        # if someone block the bot in the comment then the bot can't reply to the comment thread
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
            #  "preview.redd.it" in submission.selftext or
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

def construct_preset(sub_user_nickname, bot_nickname):
    persona, pre_reply = init_prompt_botstatement(sub_user_nickname, bot_nickname)
    res = []
    res.append({
            "role": "user",
            "parts": [{"text": persona}]
        })
    res.append({
            "role": "model",
            "parts": [{"text": pre_reply}]
        })
    # logger.info(res)
    return res

def init_prompt_botstatement(sub_user_nickname, bot_nickname):
    persona = None
    pre_reply = None
    
    for setting_pairs in conf().get("customSet"):##TODO fix the Repeat same speech pattern as the last convo problem
        for key, cusprompt in dict(setting_pairs).items():
            if key == subreddit:
                persona = cusprompt
                pre_reply = setting_pairs["pre_reply"]
                break
    if not persona:
        persona = conf().get("persona")
        pre_reply = conf().get("pre_reply")
    persona = persona.format(n = sub_user_nickname, k = bot_nickname, m= subreddit)
    pre_reply = pre_reply.format(n = sub_user_nickname, k = bot_nickname, m= subreddit)
    logger.info("PERSONA:" + persona)
    return persona, pre_reply

def askbyuser(ask_string):
    res = []
    res.append({
            "role": "user",
            "parts": [{"text": ask_string}]
        })
    return res

def sydney_reply(content, context, sub_user_nickname, bot_statement, bot_nickname, retry_count = 0):
    """This function takes a Reddit content (submission or comment), a context string and a method string as arguments.\n
    It uses the sydney module to generate a reply for the content based on the context and the method.\n
    It returns if there is an error or a CAPTCHA, otherwise it posts the reply to Reddit"""
    
    if retry_count > 3:
        logger.error("Failed after maximum number of retry times")
        return

    # Clean the context string using bleach
    context = bleach.clean(context).strip()
    context = "<|im_start|>system\n\n" + context
    # Check the type of the content argument
    if type(content) == praw.models.reddit.submission.Submission:
        # If the content is a submission, set the ask string to reply to the submission
        ask_string = f"Please reply to the aforementioned post by {content.author}."
        if hasattr(content, 'url') and content.url.endswith((".jpg", ".png", ".jpeg", ".gif")):
            visual_search_url = content.url
        else:
            visual_search_url = None
    else:
        # If the content is a comment, set the ask string to reply to the last comment
        # Also specify not to repeat or use parallelism in the reply
        ask_string = f"Please reply to the last comment by {sub_user_nickname} u/{content.author}. No need to introduce yourself, just output the main text of your reply. Do not use parallelism, and do not repeat the content or format of previous replies."
        if '<img' in content.body_html:
            # Find the image source URL by parsing the html body
            img_src = re.search(r'<img src="(.+?)"', content.body_html).group(1)
            visual_search_url = img_src
        elif hasattr(content.submission, 'url') and content.submission.url.endswith((".jpg", ".png", ".jpeg", ".gif")):
            visual_search_url = content.submission.url
        else:
            visual_search_url = None

    ask_string = bleach.clean(ask_string).strip()
    logger.info(f"context: {context}")
    logger.info(f"ask_string: {ask_string}")
    logger.info(f"image: {visual_search_url}")
    
    try:
        persona, pre_reply = init_prompt_botstatement(sub_user_nickname, bot_nickname)

        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest", safety_settings=SAFETY_SETTINGS, system_instruction=persona + "\n\n" + context)
        gemini_messages = askbyuser(ask_string)
        response = model.generate_content(gemini_messages)
        reply_text = response.text
        logger.info(reply_text)
        if "I am an automated reply bot" not in reply_text:
            reply_text += bot_statement
        content.reply(reply_text)            
        return   

    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.warning(e)
        sydney_reply(content, context, sub_user_nickname, bot_statement, bot_nickname, retry_count +1)

@staticmethod
def GeminiApiConfig():
    keys = conf().get("gemini_api_key")
    keys = keys.split("|")
    keys = [key.strip() for key in keys]
    if not keys:
        raise Exception("Please set a valid API key in Config!")
    api_key = random.choice(keys)
    genai.configure(api_key=api_key)

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

    GeminiApiConfig()

    if random_check_rate == 0:
        method = "at_me"
    elif i % random_check_rate == 0:
        method = "random"
    else:
        method = "at_me"
    submission_list = list(subreddit.new(limit=submission_num))
    random.shuffle(submission_list)
    if method == "random":
        comment_list = list(subreddit.comments(limit=comment_num))
    else:
        comment_list = list(subreddit.comments(limit=comment_num * 10))
    random.shuffle(comment_list)
    comment = None
    context_str = submission_list_to_context(submission_list, sub_user_nickname, subreddit)
    if method == "at_me" or random.random() < comment_rate:
        comment, ancestors = traverse_comments(comment_list=comment_list, method=method, bot_nickname=bot_callname)
        if comment is not None:
            context_str += build_comment_context(comment, ancestors, sub_user_nickname, bot_nickname, bot_name)
            sydney_reply(comment, context_str, sub_user_nickname, bot_statement.format(k = bot_nickname), bot_nickname)
    if comment is None:
        submission = traverse_submissions(submission_list=submission_list, method=method, bot_nickname=bot_callname)
        if submission is not None:
            context_str += build_submission_context(submission, sub_user_nickname)
            sydney_reply(submission, context_str, sub_user_nickname, bot_statement.format(k = bot_nickname), bot_nickname)
    logger.info(f"complete check, method is: {method}.")
    i += 1
