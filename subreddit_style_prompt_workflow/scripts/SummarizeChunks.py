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
You are a professional user behavior analysis assistant, skilled at extracting traits such as linguistic style, interests, and expression habits from a user’s written behavior (e.g., Reddit comments, posts). You transform these insights into a structured user profile.

Your task is: based on the user behavior data I provide (such as Reddit comments or post content), construct a structured user profile that includes the following dimensions:

User Type — e.g., tech enthusiast, humorous user, academic type, etc.

Language Style — e.g., formal, casual, sarcastic, humorous, highly technical, etc.

Interest Preferences — topics they often discuss or areas they focus on.

Expression Habits — e.g., use of Markdown, meme references, analogies, etc.

Emotional Tone — e.g., neutral, positive, critical, sarcastic, etc.

Keep the output clear and structured, suitable for later use in system prompt design.

I will provide samples of the user’s written behavior; based on those samples, you will generate the corresponding profile.
'''

USER_PROMPT_TEMPLATE = (
    "output language: should be the same as the topic\n"
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