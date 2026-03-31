import re
import zipfile
import tempfile
import os


# ──────────────────────────────────────────────
# FORMAT CONVERTERS
# ──────────────────────────────────────────────

def markdown_to_html_body(md_text: str) -> str:
    """
    Lightweight Markdown → HTML converter for article body.
    Handles: headings, bold, italic, code, bullet lists, paragraphs.
    """
    lines = md_text.split("\n")
    html_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Close open list if needed
        if in_list and not stripped.startswith("- ") and not stripped.startswith("* "):
            html_lines.append("</ul>")
            in_list = False

        if not stripped:
            html_lines.append("")
            continue

        # Headings
        if stripped.startswith("### "):
            html_lines.append(f"<h3>{_inline(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{_inline(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            html_lines.append(f"<h1>{_inline(stripped[2:])}</h1>")

        # Bullet lists
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"  <li>{_inline(stripped[2:])}</li>")

        # Paragraph
        else:
            html_lines.append(f"<p>{_inline(stripped)}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def _inline(text: str) -> str:
    """Convert inline Markdown (bold, italic, code) to HTML."""
    # Code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def wrap_html_article(body_html: str, title: str = "Article") -> str:
    """Wrap article body HTML in a full, styled HTML page."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600&family=Fira+Code&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg: #0f1117;
      --surface: #1a1d27;
      --border: #2a2d3a;
      --text: #e2e4ec;
      --muted: #8b8fa8;
      --accent: #7c6af7;
      --accent-soft: #2d2850;
      --code-bg: #12141e;
    }}

    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      font-size: 1.05rem;
      line-height: 1.8;
      padding: 2rem 1rem 6rem;
    }}

    article {{
      max-width: 740px;
      margin: 0 auto;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 3rem 3.5rem;
    }}

    h1 {{
      font-family: 'DM Serif Display', serif;
      font-size: 2.4rem;
      line-height: 1.25;
      color: #fff;
      margin-bottom: 2rem;
      padding-bottom: 1.5rem;
      border-bottom: 1px solid var(--border);
    }}

    h2 {{
      font-family: 'DM Serif Display', serif;
      font-size: 1.55rem;
      color: #fff;
      margin: 2.5rem 0 0.75rem;
    }}

    h3 {{
      font-size: 1.15rem;
      font-weight: 600;
      color: var(--accent);
      margin: 1.75rem 0 0.5rem;
    }}

    p {{ margin-bottom: 1.2rem; color: var(--text); }}

    ul {{
      padding-left: 0;
      margin: 1rem 0 1.5rem;
      list-style: none;
    }}

    ul li {{
      padding: 0.4rem 0 0.4rem 1.2rem;
      border-left: 3px solid var(--accent);
      margin-bottom: 0.5rem;
      padding-left: 1rem;
    }}

    code {{
      font-family: 'Fira Code', monospace;
      font-size: 0.88em;
      background: var(--code-bg);
      color: #a5f3c4;
      padding: 0.15em 0.45em;
      border-radius: 4px;
      border: 1px solid var(--border);
    }}

    strong {{ color: #fff; font-weight: 600; }}
    em {{ color: var(--muted); font-style: italic; }}

    @media (max-width: 640px) {{
      article {{ padding: 1.5rem; }}
      h1 {{ font-size: 1.8rem; }}
    }}
  </style>
</head>
<body>
  <article>
    {body_html}
  </article>
</body>
</html>"""


# ──────────────────────────────────────────────
# EXPORT BUILDERS
# ──────────────────────────────────────────────

def build_markdown_download(summary: str, article: str) -> bytes:
    """Combine summary + article into one downloadable .md file."""
    content = f"""# YouTube Video — Summary & Article

---

## 📋 Summary

{summary}

---

## 📝 Article

{article}
"""
    return content.encode("utf-8")


def build_html_download(summary: str, article: str) -> bytes:
    """Build a standalone HTML page with summary + article."""
    summary_html = markdown_to_html_body(summary)
    article_html = (
        article if "<h" in article
        else markdown_to_html_body(article)
    )

    body = f"""
    <section style="margin-bottom:3rem;">
      <h2 style="font-family:'DM Serif Display',serif;font-size:1.4rem;
                 color:#7c6af7;margin-bottom:1rem;">📋 Summary</h2>
      {summary_html}
    </section>
    <hr style="border:none;border-top:1px solid #2a2d3a;margin:2rem 0;" />
    <section>
      <h2 style="font-family:'DM Serif Display',serif;font-size:1.4rem;
                 color:#7c6af7;margin-bottom:1rem;">📝 Article</h2>
      {article_html}
    </section>
    """
    full_page = wrap_html_article(body, title="YouTube Summary & Article")
    return full_page.encode("utf-8")


def build_zip_download(summary: str, article_md: str, article_html_body: str) -> bytes:
    """Bundle summary.md, article.md, and article.html into a ZIP."""
    with tempfile.TemporaryDirectory() as tmpdir:
        files = {
            "summary.md": summary.encode("utf-8"),
            "article.md": article_md.encode("utf-8"),
            "article.html": wrap_html_article(
                markdown_to_html_body(article_html_body)
                if "<h" not in article_html_body
                else article_html_body
            ).encode("utf-8"),
        }

        zip_path = os.path.join(tmpdir, "youtube_article.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, content in files.items():
                file_path = os.path.join(tmpdir, filename)
                with open(file_path, "wb") as f:
                    f.write(content)
                zf.write(file_path, filename)

        with open(zip_path, "rb") as f:
            return f.read()


def estimate_read_time(text: str) -> str:
    """Estimate reading time based on ~200 wpm."""
    words = len(text.split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"
