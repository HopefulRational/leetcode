import requests
import os
import re
from bs4 import BeautifulSoup

GRAPHQL_URL = "https://leetcode.com/graphql"

QUERY = r"""
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionFrontendId
    title
    content
    difficulty
    topicTags {
      name
      slug
    }
  }
}
"""

def slug_from_input(inp: str) -> str:
    # Extract slug from input like "515. Find Largest Value in Each Tree Row"
    # Lowercase, spaces to hyphens, remove punctuation
    m = re.match(r"\s*(\d+)\.\s*(.+)", inp)
    if m:
        title = m.group(2)
    else:
        title = inp
    slug = title.strip().lower()
    slug = re.sub(r"[^a-z0-9 ]+", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug

def fetch_question(slug: str) -> dict:
    payload = {
        "operationName": "questionData",
        "variables": { "titleSlug": slug },
        "query": QUERY
    }
    r = requests.post(GRAPHQL_URL, json=payload)
    r.raise_for_status()
    return r.json()["data"]["question"]

def html_to_markdown(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Preserve code blocks and lists as-is, while converting to markdown
    # Using soup.get_text with newline seps may work but won't preserve markdown styling
    # For simplicity, return raw HTML block fenced in Markdown
    return f"\n\n<blockquote>\n\n{html}\n\n</blockquote>\n\n"

def generate_markdown(input_name: str, dest_folder: str = "."):
    slug = slug_from_input(input_name)
    data = fetch_question(slug)
    title = f"{data['questionFrontendId']}. {data['title']}"
    difficulty = data["difficulty"]
    topics = ", ".join(t["name"] for t in data["topicTags"])
    body_html = data["content"]

    md = []
    md.append(f"# [{title}](https://leetcode.com/problems/{slug}/)\n")  # Modified line
    md.append(f"**Difficulty:** {difficulty}\n")
    md.append(f"**Topics:** {topics}\n")
    md.append("---\n")
    md.append(html_to_markdown(body_html))

    filename = f"{slug}.md"
    #filename = "tmp.txt"
    path = os.path.join(dest_folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"Saved: {path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python script.py \"515. Find Largest Value in Each Tree Row\"")
        sys.exit(1)
    input_name = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else "."
    generate_markdown(input_name, ".")
