import os
import json
import tiktoken
import sys

# CONFIG
MODEL = "gpt-3.5-turbo"  # or your target model
TOKEN_LIMIT = 4096

def count_tokens(text, encoder):
    return len(encoder.encode(text))

def chunk_data(subredditname, token_limit=TOKEN_LIMIT):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    input_path = os.path.join(base_dir, "data", f"{subredditname}_data", "raw", "top_posts_last_month.json")
    output_path = os.path.join(base_dir, "data", f"{subredditname}_data", "processed", "chunks.json")
    encoder = tiktoken.encoding_for_model(MODEL)
    with open(input_path, "r", encoding="utf-8") as f:
        posts = json.load(f)

    chunks = []
    current_chunk = []
    current_tokens = 0

    for post in posts:
        post_text = f"Title: {post['title']}\nBody: {post['selftext']}\n"
        for comment in post['comments']:
            post_text += f"Comment: {comment['body']}\n"
        post_tokens = count_tokens(post_text, encoder)

        if current_tokens + post_tokens > token_limit and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0

        current_chunk.append(post)
        current_tokens += post_tokens

    if current_chunk:
        chunks.append(current_chunk)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Chunked into {len(chunks)} files for subreddit {subredditname}.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ChunkData.py <subredditname>")
        sys.exit(1)
    subredditname = sys.argv[1]
    chunk_data(subredditname)