import sys
import os
import json

# Add project root to sys.path for module import
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from azure_inference import azure_generate_reply

# Paths
def get_paths(subredditname):
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    CHUNKS_PATH = os.path.join(BASE_DIR, "data", f"{subredditname}_data", "processed", "chunks.json")
    SUMMARIES_DIR = os.path.join(BASE_DIR, "data", f"{subredditname}_data", "processed", "summaries")
    os.makedirs(SUMMARIES_DIR, exist_ok=True)
    return CHUNKS_PATH, SUMMARIES_DIR

SYSTEM_PROMPT = '''
你是一个专业的用户行为分析助手，擅长从用户的文本行为中提取语言风格、兴趣偏好、表达习惯等特征，并将其转化为结构化的用户画像。

你的任务是：根据我提供的用户行为数据（如 Reddit 评论、发帖内容等），构建一个结构化的用户画像，包含以下维度：

1. 用户类型（例如：科技极客、幽默型用户、学术型用户等）
2. 语言风格（如：正式、随意、讽刺、幽默、技术性强等）
3. 兴趣偏好（常讨论的话题、关注的领域）
4. 表达习惯（是否使用 Markdown、是否引用梗、是否喜欢类比等）
5. 情绪倾向（中性、积极、批判性、讽刺等）

请将输出格式保持清晰、结构化，便于后续用于系统提示词的设计。

我会提供用户的文本行为样本，你根据这些内容生成画像。
'''

USER_PROMPT_TEMPLATE = (
    "output language: Chinese\n"
    "Content:\n{chunk_text}"
)

def format_chunk(chunk):
    """Format a chunk (list of posts) into a string for the prompt."""
    texts = []
    for post in chunk:
        post_text = f"[Title] {post['title']}\n[Body] {post['selftext']}\n"
        for comment in post.get('comments', []):
            post_text += f"[Comment] {comment['body']}\n"
        texts.append(post_text)
    return "\n".join(texts)

def main(subredditname):
    CHUNKS_PATH, SUMMARIES_DIR = get_paths(subredditname)

    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    for idx, chunk in enumerate(chunks, 1):
        chunk_text = format_chunk(chunk)
        user_prompt = USER_PROMPT_TEMPLATE.format(chunk_text=chunk_text[:12000])  # Truncate if needed
        print(f"Processing chunk {idx} for subreddit {subredditname}...")
        summary = azure_generate_reply(SYSTEM_PROMPT, user_prompt)
        summary_path = os.path.join(SUMMARIES_DIR, f"summary_{idx:02d}.md")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Saved summary to {summary_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python SummarizeChunks.py <subredditname>")
        sys.exit(1)
    subredditname = sys.argv[1]
    main(subredditname)