# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Prompt Engineering Pipeline** that automates the lifecycle of optimizing LLM prompts for specific tasks. It pulls low-quality prompts from LangSmith Hub, refactors them using advanced prompt engineering techniques, and evaluates them against structured metrics until they meet quality thresholds (≥ 0.9 across all dimensions).

**Pipeline:** Pull → Refactor → Push → Evaluate → Iterate

## Tech Stack

- **Language:** Python 3.10+
- **Prompt Management:** LangSmith (0.2.7) for Hub integration and experimentation tracking
- **Framework:** LangChain (0.3.13) with LangChain Community and Core
- **LLM Providers:**
  - OpenAI (gpt-4o, gpt-4o-mini)
  - Google Generative AI (gemini-2.5-flash)
- **Configuration:** Pydantic (2.10.4), python-dotenv (1.0.1)
- **Testing:** pytest (8.3.4) for validation
- **Data Format:** YAML for prompt definitions, JSONL for datasets

## Project Structure

```
.
├── src/
│   ├── pull_prompts.py        # Fetch prompts from LangSmith Hub
│   ├── push_prompts.py        # Publish optimized prompts to LangSmith
│   ├── evaluate.py            # Run evaluations against dataset with custom metrics
│   ├── metrics.py             # 4 custom metric implementations (tone, acceptance, format, completeness)
│   ├── utils.py               # Helper functions (env validation, formatting, LLM selection)
│   └── __init__.py
├── tests/
│   ├── test_prompts.py        # Prompt validation tests
│   └── __init__.py
├── prompts/                   # YAML definitions of prompts (source of truth for pushing)
│   └── bug_to_user_story_v2.yml
├── datasets/                  # JSONL files for evaluation
│   └── bug_to_user_story.jsonl
├── requirements.txt           # Dependencies
├── .env                       # Environment config (create this)
└── README.md                  # Full documentation
```

## Common Development Commands

### Setup & Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

### Prompt Pipeline Operations
```bash
# 1. Pull prompts from LangSmith Hub
python src/pull_prompts.py --prompt leonanluppi/bug_to_user_story_v1

# 2. Push optimized prompts to LangSmith
python src/push_prompts.py --prompt bug_to_user_story_v2

# 3. Evaluate prompt against dataset
python src/evaluate.py --prompt davi-martins-dev/bug_to_user_story_v2 --max-examples 10

# Run full pipeline with specific LLM provider
LLM_PROVIDER=openai python src/evaluate.py --prompt owner/prompt_name
LLM_PROVIDER=google python src/evaluate.py --prompt owner/prompt_name
```

## Architecture & Key Concepts

### Phase 1: Pull (pull_prompts.py)
1. Connects to LangSmith using API key
2. Fetches prompt from Hub (format: `owner/prompt_name`)
3. Extracts message templates with roles and content
4. Serializes to YAML for local editing
5. Used as baseline for refactoring

### Phase 2: Refactor & Push (Manual + push_prompts.py)
Prompts are enhanced with:
- **Role Prompting:** Model assumes expertise (e.g., Senior Product Manager)
- **Few-shot Examples:** Multiple concrete examples covering edge cases
- **Chain-of-Thought:** Internal reasoning with checklists
- **Structured Output:** Fixed templates reduce variability
- **Enrichment:** Add business context, risks, dependencies

The optimized prompt YAML is pushed back to LangSmith as new version.

### Phase 3: Evaluate (evaluate.py)
1. **Load Dataset:** JSONL file with `inputs` (bug reports) and `outputs` (expected user stories)
2. **Execute Prompt:** Run prompt against each example
3. **Score on 4 Dimensions:**
   - **Tone Score:** Professional, empathetic language appropriate for stakeholders
   - **Acceptance Criteria Score:** Quality and testability of acceptance criteria
   - **User Story Format Score:** Adherence to "As a... I want... So that..." format
   - **Completeness Score:** Technical depth, context, and business justification
4. **Calculate Averages:** Aggregate scores across all examples
5. **Pass/Fail:** All metrics must be ≥ 0.9 to pass

### Metrics Module (metrics.py)
Each metric function takes:
- `bug_report` (input)
- `user_story` (LLM output)
- `reference` (expected output)

Returns: `{ "score": float (0-1), "reasoning": str }`

Scoring logic uses heuristics combining:
- Keyword presence (structural requirements)
- Length/depth analysis
- Semantic similarity with reference

## Environment Configuration

Create a `.env` file in project root:

```env
# LangSmith Configuration
LANGSMITH_API_KEY=lsv2_pt_xxxxx
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=desafio-prompt-engineer
LANGSMITH_TRACING=true

# LLM Provider Selection
LLM_PROVIDER=google              # or 'openai'
LLM_MODEL=gemini-2.5-flash       # or 'gpt-4o-mini'
EVAL_MODEL=gemini-2.5-flash      # or 'gpt-4o'

# API Keys (based on provider)
GOOGLE_API_KEY=AIzaSyAxxxxx      # For Google Generative AI
OPENAI_API_KEY=sk-proj-xxxxx     # For OpenAI (if using OpenAI provider)
```

**Obtain credentials:**
- LangSmith: https://smith.langchain.com/ → Create API key
- Google: https://ai.google.dev/ → Get API Key (free tier)
- OpenAI: https://platform.openai.com/api/keys/ → Create key (requires credits)

## LLM Provider Selection

The pipeline supports multiple LLM providers via environment variables:

### Option 1: Google Generative AI (Recommended for free tier)
```env
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash
EVAL_MODEL=gemini-2.5-flash
GOOGLE_API_KEY=your_key
```

### Option 2: OpenAI
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EVAL_MODEL=gpt-4o
OPENAI_API_KEY=your_key
```

Provider logic in `utils.get_llm()` handles instantiation.

## Prompt YAML Structure

Prompts are stored in `prompts/` as YAML following LangChain format:

```yaml
name: bug_to_user_story_v2
owner: davi-martins-dev
messages:
  - role: system
    content: "You are a Senior Product Manager...prompt content here"
  - role: user
    content: "Bug Report: {bug_report}"
```

When pushing, the script converts YAML to LangChain `ChatPromptTemplate`.

## Dataset Format

Evaluation datasets are JSONL (one JSON object per line):

```jsonl
{"inputs": {"bug_report": "Button doesn't work..."}, "outputs": {"reference": "As a user... expected output"}}
```

Located in `datasets/bug_to_user_story.jsonl`.

## Key Dependencies

- `langsmith`: 0.2.7 (Hub integration, experiment tracking)
- `langchain`: 0.3.13 (core framework)
- `langchain-google-genai`: 2.0.8 (Google models)
- `langchain-openai`: 0.2.14 (OpenAI models)
- `pydantic`: 2.10.4 (data validation)
- `pytest`: 8.3.4 (testing framework)

## Typical Workflow

1. **Pull** existing low-quality prompt from LangSmith Hub
2. **Analyze** performance metrics from initial evaluation
3. **Edit** the YAML prompt with improvements (role, examples, structure)
4. **Push** updated prompt to LangSmith Hub
5. **Evaluate** against dataset to see metric improvements
6. **Iterate** steps 3-5 until all metrics pass ≥ 0.9

## Troubleshooting

### Authentication errors
- Verify `LANGSMITH_API_KEY` is set correctly in `.env`
- Check API key hasn't expired
- Ensure venv is activated when running scripts

### Prompt not found (404)
- Verify prompt name format: `owner/prompt_name`
- Check if prompt was successfully pushed: `python src/push_prompts.py`
- Confirm it appears in https://smith.langchain.com/hub

### Dataset not found
- Ensure `datasets/bug_to_user_story.jsonl` exists
- Check JSONL format is valid (one JSON per line)
- Use absolute path if needed

### Import errors
- Install all requirements: `pip install -r requirements.txt`
- Ensure venv is active: `(venv)` should appear in terminal prompt

### Rate limits on LLM calls
- Reduce `--max-examples` parameter
- Add delays between evaluation runs
- Check provider account quota usage
