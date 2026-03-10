# 📐 AI Math Mentor

> A multimodal JEE-style mathematics tutor powered by **RAG · Multi-Agent LangGraph · Human-in-the-Loop · SQLite Memory**

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/YOUR_HF_USERNAME/ai-math-mentor)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-ff4b4b)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/orchestration-LangGraph-orange)](https://langchain-ai.github.io/langgraph/)

---

## ✨ Features

| Feature | Details |
|---|---|
| **3 input modes** | Text · Image (EasyOCR) · Audio (Whisper ASR) |
| **Multi-agent pipeline** | Parser → Router → Retriever → Solver → Verifier → Explainer |
| **RAG** | FAISS + `all-MiniLM-L6-v2` over a JEE knowledge base |
| **Symbolic solver** | SymPy for equations & derivatives; LLM fallback for the rest |
| **HITL** | Gates on OCR/ASR confidence < 0.6, parser ambiguity, and verifier confidence < 0.6 |
| **Memory** | SQLite store; Jaccard-similarity retrieval skips pipeline on cache hit |
| **Feedback loop** | 👍/👎 buttons + human correction field write back to memory |

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph INPUT["🎯 Multimodal Input"]
        A1[✏️ Text Input]
        A2[🖼️ Image + EasyOCR]
        A3[🎙️ Audio + Whisper ASR]
    end

    subgraph HITL_INPUT["⚠️ HITL — Input Confidence Check"]
        B["OCR / ASR Confidence < 0.6?\nShow warning + editable preview"]
    end

    subgraph MEMORY_CHECK["🗄️ Memory Lookup"]
        MC["Jaccard similarity ≥ 0.75?\nReturn cached answer"]
    end

    subgraph PIPELINE["🤖 Multi-Agent Pipeline · LangGraph"]
        C1["🔍 Parser Agent\nStructures problem → JSON\nDetects ambiguity"]
        C2["🔀 Router Agent\nClassifies topic + strategy"]
        C3["📚 Retriever Agent\nFAISS RAG — top-k chunks"]
        C4["🧮 Solver Agent\nSymPy symbolic + LLM fallback"]
        C5["✅ Verifier Agent\nChecks correctness + confidence"]
        C6["💬 Explainer Agent\nStep-by-step student explanation"]
    end

    subgraph HITL_VERIFY["⚠️ HITL — Verification Gate"]
        D["Confidence < 0.6 or\nneeds_clarification = true?\nHuman correction UI"]
    end

    subgraph OUTPUT["📊 Output"]
        E1["🎯 Final Answer · LaTeX"]
        E2["📝 Step-by-Step Explanation"]
        E3["📊 Confidence Score"]
        E4["📚 Retrieved Context Panel"]
        E5["🔀 Routing Classification"]
    end

    subgraph MEMORY_STORE["🗄️ Memory · SQLite"]
        F["Store: question, solution, explanation,\ntopic, confidence, feedback, input_type"]
        G["Retrieve: similar past problems"]
    end

    A1 & A2 & A3 --> B --> MC
    MC -->|Miss| C1
    MC -->|Hit| E1
    C1 --> C2 --> C3 --> C4 --> C5 --> C6
    C5 --> D
    C6 --> E1 & E2 & E3 & E4 & E5
    D --> E1
    E1 --> F
    G -->|Memory hit| E1
```

---

## 🚀 Quick Start

### 1 · Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/ai-math-mentor.git
cd ai-math-mentor

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2 · Configure API key

```bash
cp .env.example .env
# Edit .env and add your OpenRouter key
```

Get a free key at <https://openrouter.ai/keys>.

### 3 · Run

```bash
streamlit run app/app.py
```

The app opens at `http://localhost:8501`.

---

## 🤗 Deploying to Hugging Face Spaces

1. Create a new **Streamlit** Space at <https://huggingface.co/new-space>.
2. Push this repo to the Space:
   ```bash
   git remote add space https://huggingface.co/spaces/YOUR_HF_USERNAME/ai-math-mentor
   git push space main
   ```
3. Add `OPENROUTER_API_KEY` as a **Repository Secret** in the Space settings.
4. The Space will build automatically (~3–5 min).

---

## 📁 Project Structure

```
ai-math-mentor/
├── app/
│   └── app.py                 # Streamlit UI
├── agents/
│   ├── workflow.py            # LangGraph state machine
│   ├── parser_agent.py        # Structures raw question → JSON
│   ├── router_agent.py        # Topic + strategy classification
│   ├── solver_agent.py        # SymPy + LLM solver
│   ├── verifier_agent.py      # Confidence scoring
│   └── explainer_agent.py     # Step-by-step explanation
├── tools/
│   ├── ocr.py                 # EasyOCR wrapper (returns text + confidence)
│   ├── asr.py                 # Whisper wrapper (returns text + confidence)
│   └── sympy_solver.py        # Symbolic math helpers
├── memory/
│   └── retrieval_memory.py    # SQLite store + Jaccard retrieval
├── rag/
│   ├── retriever.py           # FAISS + sentence-transformers
│   └── build_index.py         # Index builder (run once)
├── utils/
│   ├── openrouter_llm.py      # OpenRouter API wrapper
│   ├── prompts.py             # Shared prompt templates
│   └── schemas.py             # Pydantic schemas
├── data/
│   └── knowledge_base/        # JEE topic text files (RAG corpus)
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | ✅ | OpenRouter API key — used for all LLM calls (model: `openai/gpt-4o-mini`) |

---

## 🧩 Agent Pipeline Detail

| Agent | Input | Output |
|---|---|---|
| **Parser** | Raw question string | `{problem_text, topic, variables, constraints, needs_clarification}` |
| **Router** | `problem_text` | `{topic, subtopic, strategy, use_sympy}` |
| **Retriever** | `problem_text` | `{context, sources, chunks}` via FAISS |
| **Solver** | `problem_text + context + routing` | Final answer string |
| **Verifier** | `problem_text + solution` | `{confidence, comment}` |
| **Explainer** | `problem_text + solution` | Markdown step-by-step explanation |

---

## 📊 Evaluation

See [EVALUATION.md](EVALUATION.md) for full results.

| Metric | Score |
|---|---|
| End-to-end solve accuracy (n=50) | **82%** |
| Memory hit rate (duplicate questions) | **94%** |
| HITL trigger precision | **100%** (all low-confidence cases surfaced) |
| OCR accuracy (printed equations) | **91%** |
| ASR accuracy (spoken problems) | **87%** |
| Mean response latency | **4.2 s** |

---

## 📄 License

MIT
