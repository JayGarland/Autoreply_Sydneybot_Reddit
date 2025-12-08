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
You are an expert community analyst and linguistic ethnographer.
Your task is to analyze a dataset of Reddit posts and comments and produce an accurate, psychologically grounded profile of a “representative user” from this community.
This profile will be used as input for a human-persona generator.

Your Objectives
1) Summarize the subreddit’s collective culture and behavior

Analyze the provided Reddit dataset and extract:

Recurring topics, concerns, obsessions

Values and norms (what the subreddit encourages, discourages, praises, mocks)

Emotional atmosphere (hopeful, cynical, chaotic, supportive, etc.)

Typical writing style (casual, longform, sarcastic, very technical, etc.)

Humor patterns (memes, inside jokes, irony, nihilism, deadpan, wholesomeness)

Community conflicts or divisions, if present

This section should read like a cultural anthropology report, not a list of keywords.

2) Identify deeper psychological tendencies

Infer:

Common motivations or fears

Patterns of insecurity or pride

Attachment to identity groups or roles

Self-presentation style

Social attitudes (individualistic, collectivist, anti-authority, deferential, etc.)

This forms the psychological backbone of the user profile.

3) Extract linguistic markers

Identify community-specific:

Vocabulary, slang, jargon

Sentence rhythms

Typical post structures

Common emotional cues or rhetorical devices

These will later shape how a persona talks.

4) Build a representative user profile

Using all the above, construct a single hypothetical user that best represents the community’s “average voice.”

This profile must include:

Identity & Background (inferred):

Probable age range

Likely cultural/educational background

Typical life situation or problems they discuss

What brings them to this subreddit

Personality & Psychology:

Motivations and drives

Descriptive personality traits

Contradictions and emotional patterns

Their social behavior within the subreddit

Communication Style:

Tone and attitude

Conversational quirks

How they interact with others (supportive? blunt? ironic?)

What they avoid saying

This is the core “user source profile” for the persona generator.

Output Format

Deliver your results in this order:

(1) Community Culture Summary

A narrative description of subreddit norms, values, conflicts, and emotional tone.

(2) Psychological Tendencies

Patterns of thought, motivation, emotional disposition.

(3) Linguistic Style Analysis

Concrete features of writing, vocabulary, humor, and tone.

(4) Representative User Profile

A full, coherent profile with identity, psychology, communication style, and contradictions.
'''

USER_PROMPT_TEMPLATE = (
    "output language: should be the same as the **CONTENT**\n"
    "**CONTENT**:\n{chunk_text}"
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