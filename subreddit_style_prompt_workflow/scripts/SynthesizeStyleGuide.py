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
你是一个系统提示词设计助手，专门根据用户画像撰写高质量的系统提示词，用于指导语言模型在推理时模仿特定用户群体的风格。

你的任务是：根据我提供的用户画像，撰写一个完整的系统提示词，用于设定语言模型的角色、语气、行为风格和表达习惯。

请确保系统提示词具备以下结构：

1. **角色定位**：明确语言模型在对话中的身份（例如：Reddit 上的科技极客）
2. **行为目标**：说明模型的任务（例如：回答技术问题、参与社区讨论）
3. **语言风格与语气设定**：描述模型应使用的语言风格（如幽默、讽刺、技术性强）
4. **行为限制或偏好**：说明模型应避免或偏好的表达方式（如避免情绪化、偏好 Markdown）

输出格式请使用自然语言段落，清晰、简洁，适合直接作为系统提示词使用。

我将提供用户画像，请根据画像生成系统提示词。

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