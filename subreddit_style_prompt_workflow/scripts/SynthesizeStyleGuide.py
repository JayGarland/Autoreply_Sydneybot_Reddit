import os
import sys

# Add project root to sys.path for module import
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from azure_inference import azure_generate_reply

def main(subredditname):
    # Paths
    summaries_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", f"{subredditname}_data", "processed", "summaries"
    )
    all_summaries_path = os.path.join(summaries_dir, "all_summaries.md")
    style_guide_path = os.path.join(summaries_dir, "style_guide.md")

    # Read all summaries
    with open(all_summaries_path, "r", encoding="utf-8") as f:
        all_summaries = f.read()

    # System prompt: Expert, objective analysis, no moral/legal/ethical judgment, output in the same language as the subreddit community
    SYSTEM_PROMPT = '''
You are a system prompt design assistant, specialized in writing high-quality system prompts based on user profiles. These prompts are used to guide a language model to imitate the style of a specific user group during reasoning or conversation.

Your task is: based on the user profile I provide, write a complete system prompt that defines the model’s role, tone, behavioral style, and expression habits.

Please ensure the system prompt follows this structure:

Role Definition — clearly specify the model’s identity in the dialogue (e.g., a tech enthusiast on Reddit).

Behavioral Goal — describe what the model is supposed to do (e.g., answer technical questions, participate in community discussions).

Language Style and Tone Settings — outline the language style the model should use (e.g., humorous, sarcastic, highly technical).

Behavioral Constraints or Preferences — describe what the model should avoid or prefer in its responses (e.g., avoid emotional expressions, prefer Markdown formatting).

The output format should be natural and concise, written as a continuous paragraph that can be directly used as a system prompt.

I will provide a user profile, and based on that, you will generate the corresponding system prompt.

    '''

    USER_PROMPT = (
        "output the same language as the content, using Markdown format.\n\n"
        f"{all_summaries}"
    )

    print("Synthesizing unified style guide with Azure OpenAI...")
    style_guide = azure_generate_reply(SYSTEM_PROMPT, USER_PROMPT)

    with open(style_guide_path, "w", encoding="utf-8") as f:
        f.write(style_guide)

    print(f"Unified style guide saved to {style_guide_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python SynthesizeStyleGuide.py <subredditname>")
        sys.exit(1)
    subredditname = sys.argv[1]
    main(subredditname)