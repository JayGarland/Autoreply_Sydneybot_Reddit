import os
import sys

def main(subredditname):
    # Directory containing the summaries
    summaries_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", f"{subredditname}_data", "processed", "summaries"
    )
    output_path = os.path.join(summaries_dir, "all_summaries.md")

    # Collect all summary files in order
    summary_files = [
        f"summary_{i:02d}.md" for i in range(1, 13)
    ]

    with open(output_path, "w", encoding="utf-8") as outfile:
        for fname in summary_files:
            fpath = os.path.join(summaries_dir, fname)
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8") as infile:
                    outfile.write(f"# {fname}\n\n")
                    outfile.write(infile.read())
                    outfile.write("\n\n")
            else:
                print(f"Warning: {fname} not found, skipping.")

    print(f"All summaries combined and saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python AggregateSummaries.py <subredditname>")
        sys.exit(1)
    subredditname = sys.argv[1]
    main(subredditname)