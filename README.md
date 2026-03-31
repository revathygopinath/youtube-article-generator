# 🎬 YouTube → Article

> A Streamlit app that transforms any YouTube video into a polished, structured article using a **Map-Reduce summarization pipeline** powered by **Google Gemini** and **LangChain**.

---

## ✨ Features

- **Automatic transcript fetching** — paste any YouTube URL and the app fetches the transcript automatically
- **Map-Reduce pipeline** — intelligently chunks long transcripts, summarizes each chunk independently, then reduces them into a single coherent summary
- **Smart routing** — short videos (< 3,000 tokens) skip chunking and go straight to direct summarization
- **Article generation** — converts the summary into a publication-ready article in your chosen style
- **Multiple output styles** — Blog, Newsletter, or Report
- **Flexible output formats** — Markdown or HTML
- **Summary length control** — Short, Medium, or Long
- **Export options** — download as `.md`, styled `.html`, or a `.zip` bundle of all files
- **Live progress tracking** — real-time status updates as each pipeline stage runs

---

## 🗂️ Project Structure

```
├── app.py            # Streamlit UI — layout, sidebar controls, results display
├── pipeline.py       # Core pipeline: LLM factory, Map-Reduce, article generation
├── prompts.py        # LangChain prompt templates (map, reduce, article)
├── transcript.py     # YouTube transcript fetching and token estimation
├── utils.py          # Format converters, export builders, read-time estimator
├── requirements.txt  # Python dependencies
├── _env              # Template for the .env file (rename to .env)
└── .env              # Your actual API key (not committed to version control)
```

---

## ⚙️ How It Works

The app runs a **three-stage pipeline**:

```
YouTube URL
    │
    ▼
[1] Fetch Transcript      transcript.py → YouTubeTranscriptApi
    │
    ▼
[2] Map-Reduce Summary    pipeline.py
    │   ├── MAP:    Split transcript into chunks (4,000 chars, 200 overlap)
    │   │           Each chunk → 3–5 bullet-point key ideas (Gemini)
    │   └── REDUCE: All bullet points → single coherent summary (Gemini)
    │
    ▼
[3] Article Generation    pipeline.py → generate_article()
        Summary → structured article in chosen style/format (Gemini)
```

### Short vs. Long Transcripts

| Condition | Mode | Behaviour |
|---|---|---|
| `tokens < 3,000` | `direct` | Skip chunking; pass full transcript to reduce prompt |
| `tokens ≥ 3,000` | `map-reduce` | Split into chunks, map each, then reduce |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your API key

Copy the `_env` template to `.env`:

```bash
cp _env .env
```

Then open `.env` and add your key:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

Get a free Gemini API key at: [https://aistudio.google.com/](https://aistudio.google.com/)

### 4. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 🛠️ Configuration

All options are available in the **sidebar** of the app:

| Option | Choices | Description |
|---|---|---|
| **Model** | `gemini-2.5-flash-lite`, `gemini-2.0-flash`, `gemini-2.5-flash`, `gemini-2.5-pro` | Gemini model to use. `flash-lite` has the highest free quota (1,000 req/day) |
| **Article Style** | `Blog`, `Newsletter`, `Report` | Controls tone and structure of the generated article |
| **Summary Length** | `Short`, `Medium`, `Long` | Short = 3–5 sentences · Medium = 2–3 paragraphs · Long = 4–5 paragraphs |
| **Output Format** | `Markdown`, `HTML` | Output format for both the article display and downloads |

---

## 📤 Export Options

After generation, three download options are available on the **Export** tab:

| Format | File | Contents |
|---|---|---|
| **Markdown** | `youtube_article.md` | Summary + Article in a single `.md` file |
| **HTML** | `youtube_article.html` | Fully styled standalone HTML page |
| **ZIP bundle** | `youtube_article.zip` | `summary.md` + `article.md` + `article.html` all bundled |

---

## 📦 Dependencies

```
streamlit>=1.35.0
langchain>=0.3.0
langchain-google-genai>=2.0.0
langchain-text-splitters>=0.3.0
langchain-core>=0.3.0
youtube-transcript-api>=0.6.2
google-generativeai>=0.8.0
python-dotenv>=1.0.0
```

---

## 📝 Prompt Design

Three LangChain `ChatPromptTemplate` instances drive the pipeline, defined in `prompts.py`:

### Map Prompt
Instructs the model to act as a **precise content extractor**, pulling 3–5 bullet-point key ideas from each transcript chunk. Strips all fluff: greetings, sponsor mentions, and filler phrases.

### Reduce Prompt
Instructs the model to act as an **expert summarizer**, combining all bullet-point extracts into a single, coherent prose summary. Respects the chosen length setting (Short / Medium / Long).

### Article Prompt
Instructs the model to act as a **professional content writer**, transforming the summary into a publication-ready article. Adapts its voice to the chosen style (Blog / Newsletter / Report) and outputs in the chosen format (Markdown / HTML).

---

## ⚠️ Requirements & Limitations

- The target YouTube video **must have English captions enabled**. Auto-generated captions are supported.
- Videos with **transcripts disabled** cannot be processed.
- A valid **Google Gemini API key** is required. The key is read from the `.env` file at startup.
- Very long videos with many chunks may consume significant API quota.

---

## 🔒 Security Note

The `.env` file contains your API key and **should never be committed to version control**. Add it to your `.gitignore`:

```
.env
```

The `_env` file in this repo is a safe template with no real credentials — only ever commit that.

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
