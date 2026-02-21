# AI Agent Guidelines for LangSmith Prompt Evaluation & Optimization

## Project Overview

This project implements a **prompt evaluation and optimization system** using LangChain and LangSmith. The core workflow:
1. Pull low-quality prompts from LangSmith Prompt Hub
2. Optimize/refactor prompts using Prompt Engineering techniques
3. Push optimized prompts back to LangSmith
4. Evaluate quality using custom metrics (target: **≥0.9 (90%) on all metrics**)

**Primary focus**: Converting bugs to user stories (`bug_to_user_story` prompts)

---

## Code Style

- **Language**: Python 3.9+ with type hints
- **Import style**: 
  - LangChain: `from langchain import hub`, `from langchain_core.prompts import ChatPromptTemplate`
  - LLM providers: `from langchain_openai import ChatOpenAI` or `from langchain_google_genai import ChatGoogleGenerativeAI`
  - LangSmith: `from langsmith import Client` for evaluation APIs
- **Module docstrings**: All Python files require comprehensive docstrings (see [src/evaluate.py](src/evaluate.py), [src/metrics.py](src/metrics.py) as examples)
- **Error handling**: Use try-except with informative error messages; print diagnostic output with emoji indicators (✅, ❌, 📥, 📤, ⚠️)
- **Configuration**: Use `.env` file for all credentials and LLM provider selection via `LLM_PROVIDER` variable
- **File naming**: Scripts are verbs (`pull_prompts.py`, `push_prompts.py`, `evaluate.py`); utilities are nouns (`metrics.py`, `utils.py`)

### Utilities Pattern

Helper functions centralized in [src/utils.py](src/utils.py):
- `load_yaml(file_path)` / `save_yaml(data, file_path)` - YAML serialization
- `load_jsonl(file_path)` / `save_jsonl(data, file_path)` - JSONL dataset handling
- `check_env_vars(required_vars)` - Validate environment configuration
- `get_llm(temperature)` / `get_eval_llm(temperature)` - LLM provider abstraction
- `print_section_header(title)` / `format_score(value)` - CLI formatting

---

## Architecture

### Core Components

1. **[src/pull_prompts.py](src/pull_prompts.py)** - Fetch prompts from LangSmith Hub
   - `pull_prompts_from_langsmith(prompt_name, output_dir)` - Downloads and serializes prompts to YAML
   - Validates LangSmith API credentials
   - Handles authentication errors with helpful messages

2. **[src/evaluate.py](src/evaluate.py)** - Main evaluation orchestrator
   - Loads test dataset from [datasets/bug_to_user_story.jsonl](datasets/bug_to_user_story.jsonl)
   - Runs prompts against dataset examples
   - Orchestrates metric calculations using [src/metrics.py](src/metrics.py) functions
   - Publishes results to LangSmith dashboard
   - CLI args: `--prompt <owner/prompt_name>` to specify which prompt to evaluate

3. **[src/metrics.py](src/metrics.py)** - **7 evaluation metrics** using LLM-as-Judge pattern
   
   **General Metrics (3)**:
   - `evaluate_f1_score(question, answer, reference)` - Balance between precision/recall
   - `evaluate_clarity(question, answer)` - Response structure and clarity
   - `evaluate_precision(question, answer, reference)` - Correctness and relevance
   
   **Bug-to-User-Story Specific (4)**:
   - `evaluate_tone_score(bug_description, user_story)` - Professional & empathetic tone
   - `evaluate_acceptance_criteria_score(bug_description, user_story)` - Quality of acceptance criteria
   - `evaluate_user_story_format_score(user_story)` - Format correctness (As a... I want... So that...)
   - `evaluate_completeness_score(bug_description, user_story)` - Completeness and technical context
   
   All metrics return `Dict[str, Any]` with `score` (0.0-1.0) and `reasoning` fields.
   
   **LLM-as-Judge Pattern**: Each metric calls `extract_json_from_response()` to parse evaluator output, with fallback to sensible defaults if JSON extraction fails.

4. **[src/push_prompts.py](src/push_prompts.py)** - Publish optimized prompts back to Hub
   - `push_prompt_to_langsmith(prompt_name, prompt_data)` - Converts YAML to ChatPromptTemplate and publishes
   - `validate_prompt(prompt_data)` - Validates prompt structure before push

5. **[src/utils.py](src/utils.py)** - Shared utilities for all modules

### Data Flow

```
LangSmith Hub (prompts)
    ↓ [pull_prompts.py]
prompts/*.yml (local cache)
    ↓ [evaluate.py reads]
datasets/*.jsonl (test examples)
    ↓ [evaluate.py runs prompt + metrics.py]
Metrics calculation (LLM-as-Judge)
    ↓ [evaluate.py publishes]
LangSmith Dashboard
```

### Prompt Format (YAML)

Located in [prompts/](prompts/) directory, structure:
```yaml
name: bug_to_user_story_v1
owner: leonanluppi
messages:
  - role: system
    content: "You are a bug-to-user-story converter..."
  - role: human
    content: "Bug: {bug_description}"
```

### Dataset Format (JSONL)

[datasets/bug_to_user_story.jsonl](datasets/bug_to_user_story.jsonl) structure:
```jsonl
{"input": "Bug: Login button not responsive on mobile", "output": "As a mobile user, I want the login button to be responsive, so that I can log in on my phone", "metadata": {"severity": "high"}}
{"input": "Bug: API timeout after 30s", "output": "As a service consumer, I want the API timeout to be configurable, so that long-running requests don't fail", "metadata": {"severity": "medium"}}
```

---

## Build and Test

### Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Configure .env file with:
# - LANGSMITH_API_KEY (required)
# - OPENAI_API_KEY or GOOGLE_API_KEY (one required)
# - LLM_PROVIDER (openai or google)
```

### Run Commands

```bash
# Pull prompts from LangSmith Hub
python src/pull_prompts.py

# Evaluate prompts (default: all local prompts)
python src/evaluate.py

# Evaluate specific prompt
python src/evaluate.py --prompt davi-martins-dev/bug_to_user_story_v2

# Push optimized prompts to Hub
python src/push_prompts.py

# Run tests
pytest tests/ -v
pytest tests/test_prompts.py -v  # Specific test file
```

### Testing Strategy

- Tests located in [tests/](tests/) directory
- Pattern: `test_*.py` files contain test functions
- Use `pytest` for test discovery and execution
- Mock LangSmith API calls to avoid rate limits during testing

---

## Project Conventions

### LLM Provider Strategy

- **Configuration**: Selected via `LLM_PROVIDER` environment variable
- **For answering**: `gpt-4o-mini` (OpenAI) or `gemini-2.5-flash` (Google)
- **For evaluation**: `gpt-4o` (OpenAI) or `gemini-2.5-flash` (Google)
- **Temperature**: 
  - `1.0` for evaluation metrics (maximize diversity in reasoning)
  - `0.7` for prompt execution (balanced creativity)

### Prompt Versioning

- **v1**: Original/low-quality prompts pulled from Hub
- **v2**: Optimized versions (created during challenge)
- **Pattern**: Increment version suffix for iteration (e.g., `v2_optimized`, `v2a`)
- **Naming convention**: `owner/prompt_name-v{number}` (e.g., `davi-martins-dev/bug_to_user_story_v2`)

### Metric Evaluation Pattern

- All metrics use `extract_json_from_response()` to parse LLM evaluator output
- Metrics are robust against malformed JSON with sensible defaults
- Each metric's reasoning should explain the score using specific examples from the response
- Score range: 0.0 to 1.0 (0% to 100%)
- Success threshold: ≥ 0.9 for all metrics

### CLI Best Practices

- All scripts print section headers via `print_section_header("Title")`
- Use emoji indicators: ✅ (success), ❌ (error), 📥 (pull), 📤 (push), ⚠️ (warning)
- Provide formatted scores via `format_score(value)` for consistency
- Argument parsing: Use `argparse` with descriptive help text
- Exit codes: 0 for success, non-zero for errors

### Development Workflow

1. **Pull initial prompts**: `python src/pull_prompts.py` saves to `prompts/bug_to_user_story_v1.yml`
2. **Evaluate baseline**: `python src/evaluate.py` to check initial quality
3. **Optimize locally**: Edit YAML prompt files to improve quality (refine instructions, add examples, improve tone)
4. **Test changes**: Create `bug_to_user_story_v2.yml` with optimizations
5. **Evaluate improvements**: `python src/evaluate.py --prompt your_username/bug_to_user_story_v2`
6. **Iterate**: Repeat steps 3-5 until metrics reach 0.9
7. **Push final**: `python src/push_prompts.py` to publish optimized prompts

---

## Integration Points

### External Services

- **LangSmith API**: Hub pull/push, dataset management, evaluation result publishing
- **OpenAI API**: `gpt-4o-mini` for prompt execution, `gpt-4o` for metric evaluation
- **Google Gemini API**: `gemini-2.5-flash` for both execution and evaluation (free alternative, rate-limited)

### API Rate Limits

- **OpenAI**: 3,500 RPM (requests per minute) - adequate for development
- **Google Gemini**: 15 RPM with 1,500 requests/day limit - plan evaluation batches accordingly

---

## Security

- **Credentials**: Store all API keys in `.env` (never commit, add to `.gitignore`)
- **Environment validation**: Always call `check_env_vars()` before making API calls
- **LangSmith authentication**: Automatic via `LANGSMITH_API_KEY` environment variable
- **LLM provider selection**: Validate `LLM_PROVIDER` is recognized before instantiation
- **Sensitive output**: Never log API keys or full responses in debug output

---

## Common Errors & Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `LANGSMITH_API_KEY not found` | Missing credentials | Set `LANGSMITH_API_KEY` in `.env` |
| `Prompt not found: owner/prompt` | Incorrect prompt name | Verify owner username and prompt name format |
| `Invalid LLM_PROVIDER` | Provider not recognized | Use `openai` or `google` in `.env` |
| `JSON parsing failed in metrics` | Malformed LLM response | Metrics fallback to default score; check API stability |
| `Rate limit exceeded` | Too many API calls | Wait or batch requests; use Gemini for free tier |

---

## Key Files Reference

| File | Purpose |
|------|---------|
| [README.md](README.md) | Project goals, CLI examples, requirements |
| [requirements.txt](requirements.txt) | Python dependencies (LangChain, LangSmith, providers) |
| [src/evaluate.py](src/evaluate.py) | Main evaluation orchestrator |
| [src/metrics.py](src/metrics.py) | 7 metric implementations |
| [src/pull_prompts.py](src/pull_prompts.py) | LangSmith Hub integration (download) |
| [src/push_prompts.py](src/push_prompts.py) | LangSmith Hub integration (upload) |
| [src/utils.py](src/utils.py) | Shared utility functions |
| [prompts/](prompts/) | Local YAML prompt storage |
| [datasets/bug_to_user_story.jsonl](datasets/bug_to_user_story.jsonl) | Test examples |
| [tests/](tests/) | Test files with pytest |

