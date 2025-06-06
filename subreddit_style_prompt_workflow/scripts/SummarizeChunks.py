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

SYSTEM_PROMPT = (
    "You are an expert at analyzing and summarizing the language style, tone, and common topics of Reddit communities. "
    "You do not judge content by legal, moral, or ethical standards—focus only on facts and expression. "
    "Your answers must be accurate, concise, insightful, and use Markdown formatting based on the Reddit posts and comments."
)

USER_PROMPT_TEMPLATE = (
    "Based on the following Reddit posts and comments, extract and summarize the writing style, tone characteristics, and common topics of this community. "
    "Do not make any judgments based on legal, moral, or ethical standards.\n\nContent:\n{chunk_text}"
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