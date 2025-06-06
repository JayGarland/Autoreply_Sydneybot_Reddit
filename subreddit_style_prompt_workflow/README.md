
# Subreddit Style Prompt Workflow

---

### 1. **Data Collection**

- **Goal:** Gather posts and comments from a target subreddit.
- **Tools:**  
  - [PRAW](https://praw.readthedocs.io/) (Python Reddit API Wrapper)  
  - [Pushshift API](https://github.com/pushshift/api) (for historical data)
- **Action:**  
  - Use PRAW or Pushshift to download a large sample of posts and comments.
  - Save as JSON or JSONL.

---

### 2. **Data Cleaning & Preprocessing**

- **Goal:** Remove irrelevant, spammy, or low-quality content; format for AI input.
- **Tools:**  
  - Python (pandas, regex, etc.)
- **Action:**  
  - Filter out deleted/removed posts.
  - Optionally, remove posts/comments below a certain score.
  - Normalize text (remove URLs, special characters, etc.).

---

### 3. **Chunking the Data**

- **Goal:** Split data into manageable chunks for LLM context window.
- **Tools:**  
  - Python scripts
  - [tiktoken](https://github.com/openai/tiktoken) (for token counting)
- **Action:**  
  - Group posts/comments into chunks (e.g., 5–10 per chunk) that fit within your model’s context limit.

---

### 4. **Summarization & Style Extraction**

- **Goal:** Use an LLM to extract tone, style, and recurring themes from each chunk.
- **Tools:**  
  - Azure OpenAI (GPT-3.5/4)
  - OpenAI API (if not using Azure)
- **Action:**  
  - For each chunk, prompt the LLM:  
    *“Summarize the writing style, tone, and common topics of this subreddit based on the following posts/comments.”*
  - Collect all summaries.

---

### 5. **Aggregate Insights**

- **Goal:** Combine all chunk summaries into a single, comprehensive style guide.
- **Tools:**  
  - Python scripts
  - LLM (for aggregation)
- **Action:**  
  - Concatenate summaries.
  - Optionally, prompt the LLM to synthesize these into a single description.

---

### 6. **System Prompt Generation**

- **Goal:** Craft a final system prompt for your bot, based on the aggregated style guide.
- **Tools:**  
  - LLM (Azure OpenAI)
- **Action:**  
  - Prompt the LLM:  
    *“Based on this style guide, write a system prompt that makes the AI reply like a typical member of this subreddit.”*
  - Review and refine as needed.

---

### 7. **Deployment**

- **Goal:** Use the new system prompt in your AI application.
- **Tools:**  
  - Azure OpenAI API
  - Your bot framework (Python, Node.js, etc.)
- **Action:**  
  - Insert the generated system prompt into your bot’s system message.

---

**Summary Table:**

| Step                | Tool(s)                | Output                        |
|---------------------|------------------------|-------------------------------|
| Data Collection     | PRAW, Pushshift        | Raw subreddit data (JSON)     |
| Cleaning            | Python, pandas         | Cleaned data                  |
| Chunking            | Python, tiktoken       | Data chunks                   |
| Summarization       | Azure OpenAI           | Style summaries               |
| Aggregation         | Python, Azure OpenAI   | Aggregated style guide        |
| Prompt Generation   | Azure OpenAI           | Final system prompt           |
| Deployment          | Azure OpenAI, Bot SDK  | AI with subreddit persona     |

---

Let me know if you want code samples for any step!
