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
