from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

from prompts import map_prompt, reduce_prompt, article_prompt
from transcript import estimate_tokens


# ──────────────────────────────────────────────
# LLM FACTORY
# ──────────────────────────────────────────────

def get_llm(api_key: str, model: str = "gemini-2.0-flash") -> ChatGoogleGenerativeAI:
    """Instantiate Gemini LLM via LangChain."""
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.7,
        convert_system_message_to_human=True,
        max_retries=3,
    )


# ──────────────────────────────────────────────
# TRUE MAP-REDUCE SUMMARIZATION
# ──────────────────────────────────────────────

def map_reduce_summarize(
    transcript: str,
    llm,
    length: str = "Medium",
    progress_callback=None,
) -> dict:
    """
    True Map-Reduce pipeline:

    MAP phase   — each chunk → independent mini-summary (bullet points)
    REDUCE phase — all mini-summaries → one final coherent summary

    Returns dict with keys: summary, chunk_count, mode
    """

    token_count = estimate_tokens(transcript)

    # ── Short transcript: skip chunking, go straight to reduce ──
    if token_count < 3000:
        if progress_callback:
            progress_callback(1, 1, "Summarizing (short transcript)...")

        reduce_chain = reduce_prompt | llm | StrOutputParser()
        summary = reduce_chain.invoke({
            "summaries": transcript,
            "length": length,
        })
        return {"summary": summary, "chunk_count": 1, "mode": "direct"}

    # ── Long transcript: true Map-Reduce ──
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(transcript)
    total_chunks = len(chunks)

    # Build LCEL chains
    map_chain    = map_prompt    | llm | StrOutputParser()
    reduce_chain = reduce_prompt | llm | StrOutputParser()

    # ── MAP phase: each chunk → bullet-point mini-summary ──
    mini_summaries = []
    for i, chunk in enumerate(chunks):
        if progress_callback:
            progress_callback(i + 1, total_chunks + 1, f"Mapping chunk {i+1}/{total_chunks}...")
        mini = map_chain.invoke({"chunk": chunk})
        mini_summaries.append(mini)

    # ── REDUCE phase: combine all mini-summaries → final summary ──
    if progress_callback:
        progress_callback(total_chunks + 1, total_chunks + 1, "Reducing to final summary...")

    combined = "\n\n---\n\n".join(
        f"[Section {i+1}]\n{s}" for i, s in enumerate(mini_summaries)
    )
    summary = reduce_chain.invoke({
        "summaries": combined,
        "length": length,
    })

    return {
        "summary": summary,
        "chunk_count": total_chunks,
        "mode": "map-reduce",
        "mini_summaries": mini_summaries,
    }


# ──────────────────────────────────────────────
# ARTICLE GENERATION
# ──────────────────────────────────────────────

def generate_article(
    summary: str,
    llm,
    style: str = "Blog",
    output_format: str = "Markdown",
) -> str:
    """
    Convert a summary into a structured article.
    style  : Blog | Newsletter | Report
    format : Markdown | HTML
    """
    article_chain = article_prompt | llm | StrOutputParser()
    return article_chain.invoke({
        "summary": summary,
        "style": style,
        "format": output_format,
    })


# ──────────────────────────────────────────────
# FULL PIPELINE
# ──────────────────────────────────────────────

def run_pipeline(
    transcript: str,
    api_key: str,
    model: str = "gemini-2.0-flash",
    length: str = "Medium",
    style: str = "Blog",
    output_format: str = "Markdown",
    progress_callback=None,
) -> dict:
    """
    Full pipeline: Transcript → Summary → Article

    Args:
        transcript     : Raw transcript text (already fetched)
        api_key        : Google Gemini API key
        model          : Gemini model name
        length         : Short | Medium | Long
        style          : Blog | Newsletter | Report
        output_format  : Markdown | HTML
        progress_callback : fn(step, total, message) for UI progress

    Returns dict:
        summary, article, chunk_count, mode, token_count
    """
    llm = get_llm(api_key, model)

    token_count = estimate_tokens(transcript)

    # Stage 1: Map-Reduce Summarization
    summarization_result = map_reduce_summarize(
        transcript=transcript,
        llm=llm,
        length=length,
        progress_callback=progress_callback,
    )

    # Stage 2: Article Generation
    if progress_callback:
        total = summarization_result["chunk_count"] + 2
        progress_callback(total, total, "Generating article...")

    article = generate_article(
        summary=summarization_result["summary"],
        llm=llm,
        style=style,
        output_format=output_format,
    )

    return {
        "summary": summarization_result["summary"],
        "article": article,
        "chunk_count": summarization_result["chunk_count"],
        "mode": summarization_result["mode"],
        "token_count": token_count,
        "mini_summaries": summarization_result.get("mini_summaries", []),
    }
