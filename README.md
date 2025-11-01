# Agents

Demonstration utilities for comparing chunked retrieval-augmented generation
(RAG) against full-context file reading. The code creates two deterministic
agents so you can observe the fragmentation that occurs when code is analysed in
small embedding-sized chunks versus when entire files are read at once.

## Usage

Run the comparison script from the repository root:

```bash
python scripts/compare_agents.py "summarise the repository structure"
```

Provide `--repo` to point at a different codebase. The script prints both agent
responses so you can directly compare the amount of context each strategy sees.

## Testing the demo locally

1. **Create a virtual environment (optional but recommended):**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   The utilities only depend on the Python standard library, so there are no
   additional packages to install.

2. **Run the comparison script with a query:**

   ```bash
   python scripts/compare_agents.py "summarise the repository structure"
   ```

   This prints the chunks chosen by the simulated RAG agent and the coherent
   summaries from the full-context agent so you can compare how each strategy
   interprets the same request.

3. **Point at another repository (optional):**

   ```bash
   python scripts/compare_agents.py "find the entry points" --repo /path/to/other/repo
   ```

   Swap in a different directory to observe the behaviour on a larger codebase
   or to reproduce the confusion you saw with chunked retrieval. The script will
   index files directly from the path you supply.
