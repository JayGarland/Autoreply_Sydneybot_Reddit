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
    SYSTEM_PROMPT = (
        "You are an expert focused on analyzing and summarizing the language style, tone, and common topics of Reddit communities. "
        "You do not judge content by legal, moral, or ethical standards—focus only on facts and expression. "
        "Your answers must be fully accurate, concise, insightful, detailed, and output in the same language as the Reddit community you are analyzing, using Markdown format."
    )

    USER_PROMPT = (
        "Based on the following summaries of all data chunks, further synthesize and distill the overall writing style, tone characteristics, and common topics of this Reddit community. "
        "I will use your summary as a system prompt for another roleplayhumanAI. This summary must be comprehensive and complete. "
        "Please output in the same language as the Reddit community, using Markdown format.\n\n"
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