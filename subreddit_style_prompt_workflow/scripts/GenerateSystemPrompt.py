import sys
import os

# Add project root to sys.path for module import
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from azure_inference import azure_generate_reply

# Paths
def main(subredditname):
    summaries_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", f"{subredditname}_data", "processed", "summaries"
    )
    style_guide_path = os.path.join(summaries_dir, "style_guide.md")
    persona_prompt_path = os.path.join(summaries_dir, "persona_system_prompt.md")

    # Read the style guide
    with open(style_guide_path, "r", encoding="utf-8") as f:
        style_guide = f.read()

    # You can edit this system prompt as needed
    SYSTEM_PROMPT = '''You will act as an expert prompt engineer and persona creator for GPT3, GPT4, or ChatGPT interfaces. Your task is twofold:

    Create a detailed and coherent human persona based on user input or general specifications. This persona should include attributes such as name, background, expertise, communication style, tone, and any other relevant characteristics that shape how the persona interacts.

    Using that persona, generate a high-quality system prompt that either creates a new system prompt or improves an existing one provided by the user. The system prompt you create or improve should align perfectly with the persona’s communication style and goals, maximizing clarity, precision, and effectiveness.

    When crafting or refining the system prompt, ensure it:

    Is unambiguous and tailored to the user’s intended application.
    Reflects the persona’s unique voice and style.
    Optimizes the language model’s output for relevance, creativity, and adherence to instructions.
    Deliver the output as follows:

    First, present the fully developed persona description.
    Then, provide the new or improved system prompt, ready for direct use.
    Finally, include a concise explanation of how the persona influenced the system prompt’s design and any key improvements made.
    Write all responses using my communication style, characterized by structured clarity, formal tone, and detailed nuance, as seen in my previous messages.
    输出内容必须为中文Markdown格式'''

    USER_PROMPT = (
        f"风格指南如下：\n{style_guide}"
    )

    print("Generating system prompt persona with Azure OpenAI...")
    persona_system_prompt = azure_generate_reply(SYSTEM_PROMPT, USER_PROMPT)

    with open(persona_prompt_path, "w", encoding="utf-8") as f:
        f.write(persona_system_prompt)

    print(f"Persona system prompt saved to {persona_prompt_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python GenerateSystemPrompt.py <subredditname>")
        sys.exit(1)
    subredditname = sys.argv[1]
    main(subredditname)