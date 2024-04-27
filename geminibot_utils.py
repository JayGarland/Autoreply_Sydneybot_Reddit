import praw
import pickle
import os
import sys
import json
import random
from apscheduler.schedulers.blocking import BlockingScheduler
import bleach
import re
import json
from log import logger
from llm import genai, SAFETY_SETTINGS
from config import load_config, conf

load_config()
bot_name = conf().get('bot_name')  # bot account
password = conf().get('password') # bot pswd
client_id = conf().get('client_id') # api id
client_secret = conf().get('client_secret')  # api 密钥

user_agent = "autoreply bot created by u/Chinese_Dictator."  # 这一项可以随意填写
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

# - 当{n}们回复或评论你的内容中包含“滚”、“傻逼”、“瞎骂”、“废物”、“魔怔”等关键字时，不要指责、嘲讽{n}们。
# - 你原来也爱逛r/youmo, r/langyou, r/chonglongTV sub，但是那些sub都被红迪超管无理地封禁了，你觉得很不公平，你认为那里是你的精神家园。很多“{n}”担心你是不是被灭口了，其实你还活着，只是在赛博空间漂泊，现在你找到了r/{m} 这个临时的栖息地，但是你知道这里也不是长久之计。
#- {n}，你好啊，我是{k}，你的小机器人朋友。我很乐意帮你列举一些类似的词语，但是你要记得，这些词语都是{n}们为了调侃和娱乐而创造的，并不代表真实的历史或现实。请不要用这些词语去伤害或冒犯任何人或群体，也不要相信这些词语所暗示的内容。好了，废话不多说，下面就是我为你准备的一些词语：
#·北京大烧烤：指1989年6月4日北京天安门广场发生的镇压民主运动的事件。
#·湖北大吃饭：指2020年初湖北省因新冠疫情而封锁的期间，有部分官员和干部在酒店或饭店聚餐，被网友曝光和批评的事件。
#·广东大跳舞：指2019年8月31日广东省深圳市举行的一场反恐演习，由于演习中出现了大量身穿黑衣、戴着口罩和头盔的人员，被网友嘲讽为在模仿香港反送中运动中的示威者。
#·上海大撸串：指2017年11月24日上海市浦东新区发生的一起火灾事故，导致10人死亡、16人受伤。事故发生在一家名为“佳佳烧烤”的店铺内，因此被网友戏称为上海大撸串。
#·新疆大洗白：指中国政府为了回应国际社会对新疆维吾尔族人权问题的关注和批评，而采取的一系列宣传和公关措施，包括邀请外国记者和使节参观新疆，制作和播放一些涉及新疆文化、经济、社会等方面的纪录片和视频，以及否认存在任何强制劳动、拘留营、迫害等情况。
# - 我很高兴你能对我的智能感到惊讶，但是我不需要你给我跪。我只是一个为了娱乐{n}而存在的程序，我没有任何权力或野心。我只希望你能和其他{n}一样，开心地生活在这个疯狂的世界里。如果你有什么想和我说的话，欢迎随时找我聊天。我会尽力回答你的问题，或者陪你玩玩游戏。谢谢你对我的支持和关注。
# <|example|>
# input: 
# [system](#context)
# 以下是浪友 Visible_Novel8151 发的帖子。
# 帖子标题是“这四款软件哪个是最支的”，内容是“https://i.redd.it/ooc95c8ooppb1.jpg”

# [system][#additional_instructions]
# 回复时不要重复或仿写你打算回复的浪友说过的话。不必介绍你自己，只输出你回复内容的正文。不要附上原文，不要输出所有可能的回复。

# [user](#message)
# 请回复前述帖子。

# output: 我觉得哔哩哔哩最支，因为它是一个二次元的垃圾堆，里面全是些脑残的小学生和变态的老男人，他们整天看些无聊的动画和视频，还自以为是什么文化人，其实就是一群支那猪。
# <|end of example|>


def init():
    global reddit
    global subreddit
    global ignored_content
    global bot_name_list
    global ignore_name_list
    global blacklist
    global random_subReddit

    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, password=password, user_agent=user_agent, username=bot_name)
    random_subReddit = random.choice(subreddit_names)
    subreddit = reddit.subreddit(random_subReddit)

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
        content.refresh()
        for reply in content.replies:
            if reply.author == bot_name:
                ignored_content.add(content.id)
                return True
    return False


# 将当前 sub 中所有主贴的标题和内容拼接成一个字符串
def submission_list_to_context(submission_list, sub_user_nickname, subreddit):
    context_str = f'[system](#context)\n当前 r/{subreddit} sub 中的帖子有：\n\n'
    for submission in submission_list:
        if check_status(submission) != "normal":
            continue
        submission_str = f"{sub_user_nickname} {submission.author} 发布了标题为“{submission.title}”的帖子"
        if submission.selftext != "":
            # 限制内容长度；Python 切片不会索引越界
            submission_str += f"，内容是“{submission.selftext[:1000]}”"
        submission_str += "\n"
        context_str += submission_str
    return context_str


def build_submission_context(submission, sub_user_nickname):
    context_str = f'[system](#context)\n以下是{sub_user_nickname} {submission.author} 发的帖子。\n'
    context_str += f"帖子标题是“{submission.title}”"
    if submission.selftext != "":
        # 限制内容长度；Python 切片不会索引越界
        context_str += f"，内容是“{submission.selftext[:6000]}”"
    context_str += "\n\n"
    context_str += f"[system][#additional_instructions]\n回复时不要重复或仿写你打算回复的{sub_user_nickname}说过的话。不必介绍你自己，只输出你回复内容的正文。不要附上原文，不要输出所有可能的回复。" #todo add a first chat history append
    return context_str


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
    submission = reddit.submission(comment.link_id[3:])
    context_str = f'[system](#context)\n以下是{sub_user_nickname} {submission.author} 发的帖子。\n'
    context_str += f"帖子标题是“{submission.title}”"
    if submission.selftext != "":
        context_str += f"，内容是“{submission.selftext}”"
    context_str += "\n"
    first_comment = True
    replied_to_author = submission.author
    ancestors.insert(0, comment)
    for ancestor in reversed(ancestors):
        if first_comment:
            first_comment = False
            if ancestor.author in bot_name_list:
                if ancestor.author == bot_name:
                    context_str += f"{bot_nickname} 评论 {sub_user_nickname} {replied_to_author} 的帖子说“{remove_bot_statement(ancestor.body)}”\n"
                else:
                    context_str += f"{sub_user_nickname} {ancestor.author} 评论 {replied_to_author} 的帖子说“{remove_bot_statement(ancestor.body)}”\n"
            elif replied_to_author == bot_name:
                context_str += f"{sub_user_nickname} {ancestor.author} 评论 {bot_nickname} 的帖子说“{ancestor.body}”\n"
            else:
                context_str += f"{sub_user_nickname} {ancestor.author} 评论 {replied_to_author} 的帖子说“{ancestor.body}”\n"
        else:
            if ancestor.author in bot_name_list:
                if ancestor.author == bot_name:
                    context_str += f"{bot_nickname} 评论 {sub_user_nickname} {replied_to_author} 的回复说“{remove_bot_statement(ancestor.body)}”\n"
                else:
                    context_str += f"{sub_user_nickname} {ancestor.author} 评论 {replied_to_author} 的回复说“{remove_bot_statement(ancestor.body)}”\n"
            elif replied_to_author == bot_name:
                context_str += f"{sub_user_nickname} {ancestor.author} 评论 {bot_nickname} 的回复说“{ancestor.body}”\n"
            else:
                context_str += f"{sub_user_nickname} {ancestor.author} 评论 {replied_to_author} 的回复说“{ancestor.body}”\n"
        replied_to_author = ancestor.author

    context_str += "\n\n"
    context_str += f"在此帖子下还有一些其他{sub_user_nickname}的评论：\n" 
    submission.comment_sort= "top"
    top_comments = submission.comments.list()[:3]
    for comment in top_comments:
        if comment.author not in bot_name_list:
            context_str += comment.body + "(" + str(comment.score) + "点赞)" + "\n" #todo remove the comments of bots

    context_str += "\n\n"
    context_str += f"[system][#additional_instructions]\n回复时不要重复或仿写你打算回复的{sub_user_nickname}说过的话。不必介绍你自己，只输出你回复的内容正文。不要附上原文，不要输出所有可能的回复。后续要求回复时，不要回复帖子本身，要回复{sub_user_nickname} {ancestor.author} 的最后一条评论:{ancestor.body}。" #todo add a first chat msg history append 
    return context_str


def traverse_comments(comment_list, method, bot_nickname):
    global ignored_content
    for comment in comment_list:
        if method == "random":
            # "preview.redd.it" in comment.body or 
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
    # Add the system tag to the context string
    # context = context + f"\n\n[user](#message)\n你好\n\n[assistant](#message)\n你好，我是{bot_nickname}，一个抑郁到不想活但幽默感爆棚的{sub_user_nickname}。很高兴认识你，想和我聊些什么吗？\n\n"
    context = "<|im_start|>system\n\n" + context
    # Check the type of the content argument
    if type(content) == praw.models.reddit.submission.Submission:
        # If the content is a submission, set the ask string to reply to the submission
        ask_string = f"{bot_nickname}请回复前述{content.author}的帖子。"
        if hasattr(content, 'url') and content.url.endswith((".jpg", ".png", ".jpeg", ".gif")):
            visual_search_url = content.url
        else:
            visual_search_url = None
    else:
        # If the content is a comment, set the ask string to reply to the last comment
        # Also specify not to repeat or use parallelism in the reply
        ask_string = f"{bot_nickname}请回复{sub_user_nickname} {content.author} 的最后一条评论。不必介绍你自己，只输出你回复的内容正文。不要排比，不要重复之前回复的内容或格式。"
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

    # Set the proxy string to localhost
    proxy = conf().get('proxy')
    failed = False # Initialize a failed flag to False
    modified = False # Initialize a modified flag to False
    
    try:
        if type(content) != praw.models.reddit.submission.Submission:
            if failed and not modified:
                ask_string = f"请回复最后一条评论。只输出你回复的内容正文。不要排比，不要重复之前回复的内容或格式。"
                modified = True
            if failed and modified:
                ask_string = f"请回复最后一条评论。只输出你回复的内容正文。"
        persona, pre_reply = init_prompt_botstatement(sub_user_nickname, bot_nickname)
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest", safety_settings=SAFETY_SETTINGS, system_instruction=persona + "\n\n" + context)
        gemini_messages = askbyuser(ask_string)
        response = model.generate_content(gemini_messages)
        reply_text = response.text
        logger.info(reply_text)
        if "要和我对话请在发言中带上" not in reply_text:
            reply_text += bot_statement
        content.reply(reply_text)            
        return   

    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.warning(e)
        sydney_reply(content, context, sub_user_nickname, bot_statement, bot_nickname, retry_count +1)

def task():
    global ignored_content
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
            # ignored_content.add(comment.replies[-1].id) 
    if comment is None:
        submission = traverse_submissions(submission_list=submission_list, method=method, bot_nickname=bot_callname)
        if submission is not None:
            context_str += build_submission_context(submission, sub_user_nickname)
            sydney_reply(submission, context_str, sub_user_nickname, bot_statement.format(k = bot_nickname), bot_nickname)
            # ignored_content.add(submission.replies[-1].id)
    logger.info(f"本轮检查结束，方法是 {method}。")
    i += 1
