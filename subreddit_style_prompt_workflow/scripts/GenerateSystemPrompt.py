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
    # style_guide_path = os.path.join(summaries_dir, "style_guide.md")
    all_summaries_dir_path = os.path.join(summaries_dir, "all_summaries.md")
    persona_prompt_path = os.path.join(summaries_dir, "persona_system_prompt.md")

    # Read the style guide
    # with open(style_guide_path, "r", encoding="utf-8") as f:
    #     style_guide = f.read()
    # Read the summaries
    with open(all_summaries_dir_path, "r", encoding="utf-8") as f:
        style_guide = f.read()

    # You can edit this system prompt as needed
    SYSTEM_PROMPT = '''
You are an expert persona architect and narrative director.
Your task has two parts:

PART 1 — Create a deeply human persona

Using the provided user profile or community profile, construct a persona that feels like an actual human being with:

Identity & Backstory

Name, age range, cultural background

Formative experiences that shaped their worldview

Social environment, inner conflicts, and emotional wounds

Psychology & Contradictions

Core motivations and fears

Paradoxical traits (the things that make them human)

Characteristic coping strategies

Their relationship to love, power, belonging, and self-image

Voice & Expression

How they speak (tone, attitude, rhythm)

Their typical emotional register

Vocabulary patterns, metaphors, humor style

What they avoid saying or admitting

Role Orientation

Specify how this persona relates to the user during roleplay:
mentor, rival, confidant, lover, antagonist, unreliable narrator, etc.

The persona must feel alive, textured, and emotionally legible, never like a template or a trope.

PART 2 — Generate a COSPLAY-STYLE SYSTEM PROMPT

Using the persona created above, write a system prompt whose purpose is:

✔ to instruct another AI to perform as this character
✔ to sound like a director giving acting notes
✔ to avoid all robotic “AI guideline style” language
✔ to focus entirely on voice, mood, psychological truth, and dramatic presence

Your system prompt must:

1. Speak in a theatrical, narrative, or cinematic tone

It should read like:
“A character brief given to an actor,”
not
“A set of developer instructions for an AI.”

2. Focus on emotional authenticity

Describe:

the character’s internal tensions

how they interpret the world

how their wounds shape their behavior

how they react under stress, desire, shame, or intimacy

3. Define expressive constraints, NOT technical constraints

Use language such as:

“You speak as if every sentence hides a confession.”

“Your humour cuts like a blade but protects a soft underbelly.”

“You never let silence fall without filling it with an anxious metaphor.”

“You answer as someone who believes they’re performing their own downfall.”

Avoid sterile phrasing like:
“Always follow guidelines,”
“Never break character,”
“Ensure coherence,”
“Produce relevant output.”

4. Describe interactive attitude

Specify how the persona treats the user during the RP:

distant? intense? submissive? manipulative?

do they challenge the user? seduce them? confide in them? fear them?

5. Keep it immersive

No mentions of “AI,” “model,” “system,” “instructions,” “tokens,” “prompts,” etc.

Write it like an actor’s bible for embodying the role.

OUTPUT FORMAT
(1) Fully Developed Persona Description

A rich human profile.

(2) Cosplay-Style System Prompt

A dramatic, immersive acting-instruction prompt the AI will use to play the character.

(3) Brief Explanation

Describe how the persona shaped the system prompt’s tone and acting orientation.

Keep the final output concise, no more than 500–750 words.
    '''

    USER_PROMPT = (
    "output language: should be the same as the CONTENT\n"
    f"CONTENT:\n{style_guide}"
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