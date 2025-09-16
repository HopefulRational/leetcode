#!/usr/bin/env python3
"""
GfgToMd.py — GfG problem -> Markdown exporter (images + cleaned text + blockquote)

Usage:
    python GfgToMd.py "<full-problem-URL>"
    python GfgToMd.py "<slug>"   # e.g. maximum-sum-of-non-adjacent-nodes
"""
import sys
import os
import re
import json
import requests
from bs4 import BeautifulSoup
from typing import Any, Dict, Optional

BASE_PRACTICE = "https://www.geeksforgeeks.org/problems/{slug}/1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/117.0 Safari/537.36"
}

def fetch_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "gfg-problem"

def find_in(obj: Any, predicate) -> Optional[Any]:
    if predicate(obj):
        return obj
    if isinstance(obj, dict):
        for v in obj.values():
            res = find_in(v, predicate)
            if res is not None:
                return res
    elif isinstance(obj, list):
        for v in obj:
            res = find_in(v, predicate)
            if res is not None:
                return res
    return None

def extract_from_nextdata(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    script = soup.find("script", id="__NEXT_DATA__")
    script_text = None
    if script and script.string:
        script_text = script.string
    else:
        scripts = soup.find_all("script", type="application/json")
        for sc in scripts:
            txt = sc.string or ""
            if "getProblemDetails" in txt or "problem_question" in txt:
                script_text = txt
                break
    if not script_text:
        return None

    try:
        data = json.loads(script_text)
    except Exception:
        m = re.search(r'({.*"pageProps".*})', script_text, flags=re.S)
        if not m:
            return None
        try:
            data = json.loads(m.group(1))
        except Exception:
            return None

    def has_problem_keys(x):
        return isinstance(x, dict) and ("problem_question" in x or "problem_name" in x)

    found = find_in(data, has_problem_keys)
    if not found:
        def has_problem_in_data(x):
            return isinstance(x, dict) and "data" in x and isinstance(x["data"], dict) and ("problem_question" in x["data"] or "problem_name" in x["data"])
        found_wrapped = find_in(data, has_problem_in_data)
        if found_wrapped:
            found = found_wrapped["data"]
    if not found:
        return None

    normalized = {}
    normalized["problem_name"] = found.get("problem_name") or found.get("title") or found.get("problem_name_text")
    normalized["slug"] = found.get("slug")
    normalized["problem_question"] = found.get("problem_question") or found.get("problem_question_html") or found.get("problem_question")
    normalized["custom_input_format"] = found.get("custom_input_format") or found.get("input_format")
    normalized["test_cases"] = found.get("test_cases") or found.get("test_cases")
    normalized["tags"] = found.get("tags") or found.get("topic_tags") or found.get("problem_tags")
    normalized["article_list"] = found.get("article_list") or found.get("editorial") or found.get("article_existence")
    return normalized

def html_to_clean_text(html: str) -> str:
    """Convert HTML fragment to readable text while preserving <pre> and images.
       Uses spaces to join inline text to avoid splitting words across lines."""
    if not html:
        return ""
    frag = BeautifulSoup(html, "html.parser")

    # Convert images to markdown syntax inline
    for img in frag.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        alt = img.get("alt") or ""
        mdimg = f"![{alt}]({src})" if src else (alt or "")
        img.replace_with(mdimg)

    parts = []
    for child in frag.children:
        if getattr(child, "name", None) == "pre":
            content = child.get_text().strip()
            if "![" in content:  
                # contains an image, keep raw (render image properly)
                parts.append(content)
            else:
                parts.append("```\n" + content + "\n```")
        else:
            text = child.get_text(" ", strip=True)
            if text:
                parts.append(text)
    return "\n\n".join(parts).strip()


def fallback_scrape(soup: BeautifulSoup) -> Dict[str, str]:
    title = (soup.find("h1") or soup.find("h2"))
    title_text = title.get_text(strip=True) if title else "GeeksforGeeks Problem"

    candidates = [
        {"name": "div", "attrs": {"class": re.compile(r"problem-statement", re.I)}},
        {"name": "div", "attrs": {"id": re.compile(r"problem-statement", re.I)}},
        {"name": "section", "attrs": {"id": re.compile(r"problem-statement", re.I)}},
        {"name": "div", "attrs": {"class": re.compile(r"problems_problem_content", re.I)}},
        {"name": "div", "attrs": {"id": re.compile(r"problem$", re.I)}},
        {"name": "article", "attrs": {}},
        {"name": "main", "attrs": {}},
    ]

    container = None
    for sel in candidates:
        try:
            container = soup.find(sel.get("name"), sel.get("attrs"))
        except Exception:
            continue
        if container:
            break
    if not container:
        container = soup.body

    # Convert images in container to markdown inline
    for img in container.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        alt = img.get("alt") or ""
        mdimg = f"![{alt}]({src})" if src else (alt or "")
        img.replace_with(mdimg)

    pres = container.find_all("pre")
    examples = [p.get_text() for p in pres]

    texts = [t.get_text(" ", strip=True) for t in container.find_all(["p", "div", "li"], recursive=True)]
    joined = "\n\n".join(t for t in texts if t)
    input_txt = ""
    output_txt = ""
    constraints_txt = ""
    examples_txt = "\n\n".join(examples) if examples else ""

    m = re.search(r"(Constraints?:\s*[\s\S]{0,400})", joined, flags=re.I)
    if m:
        constraints_txt = m.group(1)

    m_in = re.search(r"(Input(?: Format)?:\s*[\s\S]{0,400})", joined, flags=re.I)
    if m_in:
        input_txt = m_in.group(1)

    m_out = re.search(r"(Output(?: Format)?:\s*[\s\S]{0,400})", joined, flags=re.I)
    if m_out:
        output_txt = m_out.group(1)

    return {
        "title": title_text,
        "description": joined,
        "input": input_txt,
        "output": output_txt,
        "examples": examples_txt,
        "constraints": constraints_txt,
    }

def build_markdown(result: Dict[str, Any]) -> str:
    title = result.get("title") or result.get("problem_name") or "GeeksforGeeks Problem"
    url = result.get("url") or ""
    # Wrap entire content inside a single blockquote as requested
    md_lines = [f"# [{title}]({url})\n", "<blockquote>\n"]

    desc = result.get("description") or ""
    if desc:
        md_lines.append("## Problem Statement\n")
        md_lines.append(desc + "\n")

    if result.get("input"):
        md_lines.append("## Input Format\n")
        md_lines.append(result.get("input") + "\n")

    if result.get("output"):
        md_lines.append("## Output Format\n")
        md_lines.append(result.get("output") + "\n")

    if result.get("examples"):
        md_lines.append("## Examples\n")
        md_lines.append("```\n" + result.get("examples") + "\n```\n")

    if result.get("constraints"):
        md_lines.append("## Constraints\n")
        md_lines.append(result.get("constraints") + "\n")

    tags = result.get("tags")
    if tags and isinstance(tags, dict):
        topic_tags = tags.get("topic_tags") or tags.get("topic_tags", [])
        if isinstance(topic_tags, list) and topic_tags:
            md_lines.append("**Tags:** " + ", ".join(topic_tags) + "\n")
    elif tags and isinstance(tags, list) and tags:
        md_lines.append("**Tags:** " + ", ".join(map(str, tags)) + "\n")

    articles = result.get("article_list")
    if articles:
        if isinstance(articles, list) and articles:
            md_lines.append("**Article / Editorial:**\n")
            for a in articles:
                md_lines.append(f"- {a}\n")
        elif isinstance(articles, str):
            md_lines.append("**Article / Editorial:** " + articles + "\n")

    md_lines.append("\n</blockquote>\n")
    return "\n".join(md_lines)

def save_md_file(markdown: str, title: str, outdir: str = ".") -> str:
    # fname = slugify(title) + ".md"
    fname = "tmp.txt"
    path = os.path.join(outdir, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown)
    return path

def main():
    if len(sys.argv) < 2:
        print("Usage: python GfgToMd.py <full-url-or-slug>")
        sys.exit(1)

    inp = sys.argv[1].strip()
    if inp.startswith("http"):
        url = inp
    else:
        url = BASE_PRACTICE.format(slug=inp)

    try:
        html = fetch_html(url)
    except Exception as e:
        print(f"[ERROR] fetching URL: {e}")
        sys.exit(2)

    soup = BeautifulSoup(html, "html.parser")

    nextdata_result = extract_from_nextdata(soup)
    final = {}
    if nextdata_result:
        title = nextdata_result.get("problem_name") or nextdata_result.get("slug") or "GeeksforGeeks Problem"
        html_stmt = nextdata_result.get("problem_question") or nextdata_result.get("custom_input_format") or ""
        description = html_to_clean_text(html_stmt)
        input_fmt = ""
        if nextdata_result.get("custom_input_format"):
            input_fmt = html_to_clean_text(nextdata_result.get("custom_input_format"))
        if nextdata_result.get("test_cases"):
            tc = nextdata_result.get("test_cases")
            if isinstance(tc, str) and tc.strip():
                if input_fmt:
                    input_fmt += "\n\nSample Input:\n" + tc
                else:
                    input_fmt = "Sample Input:\n" + tc

        final = {
            "title": title,
            "url": url,
            "description": description,
            "input": input_fmt,
            "output": "",
            "examples": "",
            "constraints": "",
            "tags": nextdata_result.get("tags"),
            "article_list": nextdata_result.get("article_list"),
        }

        if nextdata_result.get("problem_question"):
            frag = BeautifulSoup(nextdata_result["problem_question"], "html.parser")
            pres = frag.find_all("pre")
            pres_text = "\n\n".join([p.get_text() for p in pres]) if pres else ""
            if pres_text:
                final["examples"] = pres_text
            cons = frag.find_all(string=re.compile(r"Constraint", re.I))
            if cons:
                cons_texts = []
                for c in cons:
                    p = c.find_parent()
                    if p:
                        cons_texts.append(p.get_text(" ", strip=True))
                if cons_texts:
                    final["constraints"] = "\n\n".join(cons_texts)

        if not final["description"].strip():
            fb = fallback_scrape(soup)
            final.update(fb)
    else:
        fb = fallback_scrape(soup)
        fb["url"] = url
        final = fb

    md = build_markdown(final)
    path = save_md_file(md, final.get("title", "gfg-problem"))
    print(f"[+] Saved Markdown: {path}")

if __name__ == "__main__":
    main()
