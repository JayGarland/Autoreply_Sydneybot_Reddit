import os
import sys
import subprocess

def main(subreddit):
    script_dir = os.path.dirname(__file__)
    steps = [
        "DataCollection.py",
        "ChunkData.py",
        "SummarizeChunks.py",
        "AggregateSummaries.py",
        # "SynthesizeStyleGuide.py",
        "GenerateSystemPrompt.py"
    ]
    for idx, script in enumerate(steps, 1):
        print(f"[{idx}/{len(steps)}] Running {script} for subreddit '{subreddit}'...")
        result = subprocess.run([
            sys.executable,
            os.path.join(script_dir, script),
            subreddit
        ])
        if result.returncode != 0:
            print(f"Error: {script} failed.")
            sys.exit(result.returncode)
    print("Workflow completed successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <subreddit>")
        sys.exit(1)
    subreddit = sys.argv[1]
    main(subreddit)