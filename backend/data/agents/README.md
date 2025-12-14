# Agent Datasets

Place your fine-tuning datasets here, one folder per agent. Example structure:

```text
backend/
  data/
    agents/
      sales/
        train.jsonl
        eval.jsonl
      verification/
        train.jsonl
      underwriting/
        train.jsonl
      sanction/
        train.jsonl
```

Each `train.jsonl` should be a JSONL file with records like:

```json
{"instruction": "User asks for a 5L personal loan", "input": "", "output": "Model answer in your desired style"}
```

You can fine-tune a base Ollama model per agent using Unsloth or your preferred PEFT library, then register the resulting model with Ollama and set the corresponding env vars, for example:

- `OLLAMA_MODEL_MASTER=intelliapprove-master`
- `OLLAMA_MODEL_SALES=intelliapprove-sales`
- `OLLAMA_MODEL_VERIFICATION=intelliapprove-verification`
- `OLLAMA_MODEL_UNDERWRITING=intelliapprove-underwriting`
- `OLLAMA_MODEL_SANCTION=intelliapprove-sanction`

The backend will automatically use these model names when `LLM_PROVIDER=ollama` is configured.