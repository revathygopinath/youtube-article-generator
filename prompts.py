from langchain_core.prompts import ChatPromptTemplate

# ──────────────────────────────────────────────
# MAP PROMPT — summarize each individual chunk
# ──────────────────────────────────────────────

MAP_SYSTEM = """You are a precise content extractor. Your only job is to pull out
the essential information from a portion of a YouTube transcript.
Strip all fluff: greetings, subscribe reminders, sponsor mentions, filler phrases."""

MAP_HUMAN = """Extract the key ideas from this transcript chunk.

OUTPUT FORMAT:
- 3 to 5 bullet points only
- Each bullet = one distinct idea, fact, step, or insight
- Preserve any technical terms, code, tools, commands exactly
- Skip anything promotional, repetitive, or off-topic

TRANSCRIPT CHUNK:
{chunk}

KEY POINTS:
"""

map_prompt = ChatPromptTemplate.from_messages([
    ("system", MAP_SYSTEM),
    ("human", MAP_HUMAN),
])


# ──────────────────────────────────────────────
# REDUCE PROMPT — combine all chunk summaries
# ──────────────────────────────────────────────

REDUCE_SYSTEM = """You are an expert summarizer. You receive bullet-point extracts
from multiple sections of a YouTube video and synthesize them into one
coherent, polished summary. You never add information not present in the input."""

REDUCE_HUMAN = """Combine the following key points from all sections of a YouTube video
into a single unified summary.

SUMMARY LENGTH: {length}
- Short  → 3–5 sentences, only the most critical takeaways
- Medium → 2–3 paragraphs, covering main ideas with light detail
- Long   → 4–5 paragraphs, comprehensive with supporting details

RULES:
- Write in clear, flowing prose (not bullet points)
- Group related ideas into logical paragraphs
- Preserve all technical terms, tools, code, and commands exactly
- Do NOT add opinions, commentary, or information not in the input
- Do NOT mention "this video", "the speaker", or "the transcript"

ALL EXTRACTED KEY POINTS:
{summaries}

FINAL SUMMARY:
"""

reduce_prompt = ChatPromptTemplate.from_messages([
    ("system", REDUCE_SYSTEM),
    ("human", REDUCE_HUMAN),
])


# ──────────────────────────────────────────────
# ARTICLE PROMPT — convert summary → article
# ──────────────────────────────────────────────

ARTICLE_SYSTEM = """You are a professional content writer who specializes in
transforming raw summaries into polished, publication-ready articles.
You adapt your voice perfectly to the requested style."""

ARTICLE_HUMAN = """Write a complete, well-structured article based on the summary below.

ARTICLE STYLE: {style}

Style guidelines:
- Blog      : Conversational and engaging. Use relatable language, subheadings,
               short paragraphs. End with a takeaway or call-to-action.
- Newsletter: Scannable and concise. Use a "What You Need to Know" intro block,
               short punchy sections, and a "Bottom Line" closing.
- Report    : Formal and objective. Numbered sections, precise language,
               no conversational filler. End with a structured Conclusion.

OUTPUT FORMAT: {format}

If format is Markdown:
- Use # for title, ## for sections, ### for subsections
- Use **bold** for key terms, `backticks` for code/commands
- Use bullet lists where appropriate

If format is HTML:
- Output ONLY the content inside <body> — no <html>, <head>, or <style> tags
- Use semantic tags: <article>, <h1>, <h2>, <h3>, <p>, <ul>, <li>, <code>, <strong>
- Add class="highlight" on any <code> or key term spans

SUMMARY TO USE:
{summary}

ARTICLE:
"""

article_prompt = ChatPromptTemplate.from_messages([
    ("system", ARTICLE_SYSTEM),
    ("human", ARTICLE_HUMAN),
])
