# Hi, I'm Christina Norman

I'm a 20+ year games industry veteran (BioWare - Mass Effect 1-3, Riot Games - League of Legends, Wild Rift) and entrepreneur (Founder: Elodie Games) My strengths include game engineering, game design, and studio leadership.

## Current Focus

- Consultant focused on increasing developer productivity by creating AI-enhanced workflows (Amazon, Spryfox, Roboto Games)
- Improving performance of locally hosted LLM infrastructure (VLLM), GGUF model support, memory optimization, inference performance.

## Articles

Articles I've written on Claude Code and developer productivity.

- [The Claude Code Information Hierarchy](https://dev.to/kitaekatt/the-claude-code-information-hierarchy-5b3o-temp-slug-2941549)
- [Mastering Cache Hits in Claude Code](https://dev.to/kitaekatt/mastering-cache-hits-in-claude-code-5648)

## Claude and Open Source Contributions

### Claude Plugins

[**plugins-kit**](https://kitaekatt.github.io/plugins-kit/) — a Claude Code plugin marketplace focused on enabling richer, more powerful plugins to be deployed in a team environment. The core `bootstrap` plugin lets any plugin with a properly configured `bootstrap.json` auto-configure its own software and library dependencies (install missing binaries, Python packages, etc.) so contributors don't have to hand-set-up each tool. Includes games-industry focused plugins like `unreal-kit` and `p4-kit` that improve Claude's ability to work within common games-industry toolchains.

- **bootstrap** — dependency management for plugins; any plugin with a `bootstrap.json` can declare and install what it needs.
- **skills-kit** — a robust skill development framework with new skill features.
- **unreal-kit** — makes it easier for Claude to work with Unreal.
- **p4-kit** — local code review of Perforce changelists.
- **awesome-kit** — a collection of awesome skills.

### Claude Code

As an active contributor to Anthropic's Claude Code project, I've filed feature requests and submitted bug reports that have resulted in tangible improvements to the developer experience.

<details>
<summary>2 feature requests implemented</summary>

1. [#19541](https://github.com/anthropics/claude-code/issues/19541) — Per-terminal session affinity for --continue.
`--continue` resumed the most recent session globally, breaking multi-terminal workflows — restarting in one terminal would pick up a different terminal's session. Filed a proposal with a terminal identifier priority table covering iTerm, Kitty, Windows Terminal, tmux, and others. Sessions now display a resume command with session ID on exit (e.g. `claude --resume <session-id>`), giving users explicit control over which session to continue.
2. [#13412](https://github.com/anthropics/claude-code/issues/13412) — "Shell cwd was reset" message noise.
Users working across multiple repositories from a central config repo saw this message after every Bash command run outside the project root, making output hard to read. Filed a request to make it suppressible. Fixed by @ltawfik.

</details>

<details>
<summary>2 bugs reported and fixed</summary>

1. [#20409](https://github.com/anthropics/claude-code/issues/20409) — Silent plugin skill registration failure.
Unknown fields in plugin.json caused skills to silently fail to register — the plugin appeared loaded but skills weren't discoverable, with no error surfaced. Filed a report with a disclosure principles framework and proposal for warning badges and /doctor integration. Fixed by @blois.
2. [#12031](https://github.com/anthropics/claude-code/issues/12031) — PreToolUse hooks stripped AskUserQuestion answers.
Any active PreToolUse hook caused the user's selection to be silently dropped. Filed a detailed report with a testing matrix isolating the bug to PreToolUse specifically (PostToolUse and SessionStart were unaffected). Fixed in v2.0.76.

</details>

### [vLLM](https://github.com/vllm-project/vllm) (High-throughput LLM Inference Engine)

While working to get Gemma2, Gemma3, and other quantized models loading and running correctly in vLLM — particularly on Blackwell hardware (RTX 5090) — I traced and fixed a series of bugs in the GGUF backend: multi-process hangs, config mapping gaps, dtype conflicts, weight loading errors, and missing architecture support.

<details>
<summary>3 PRs merged</summary>

1. [#30209](https://github.com/vllm-project/vllm/pull/30209) — Skip generation config fallback for GGUF to prevent multi-process hang.
Loading GGUF models in multi-process mode (V1 engine) caused an indefinite hang — both the EngineCore and APIServer processes tried to memory-map the same GGUF file. Fix skips the fallback entirely since GGUF files embed config in the file header.

2. [#30407](https://github.com/vllm-project/vllm/pull/30407) — Add memory barriers for cross-process shared memory visibility.
Shared memory broadcast caused data races across process boundaries in multi-process inference. Added ordering guarantees to ensure correct visibility of shared state.

3. [#30408](https://github.com/vllm-project/vllm/pull/30408) — Disable bfloat16 for GGUF on Blackwell.
GGUF models on Blackwell GPUs (RTX 5090, SM 120+) produced incorrect output because bfloat16 causes precision issues with quantized weights on this architecture. Fix defaults GGUF to float16 on Blackwell with a warning when bfloat16 is explicitly requested.

</details>

<details>
<summary>5 PRs open</summary>

1. [#30410](https://github.com/vllm-project/vllm/pull/30410) — Auto-select compatible dtype for GGUF on Blackwell.
Gemma2/Gemma3 GGUF models on Blackwell hit a dtype deadlock: float16 causes numerical instability in Gemma, bfloat16 causes precision issues with GGUF on Blackwell. Fix adds `_resolve_dtype_conflict()` to auto-select float32 when both are disallowed.

2. [#30412](https://github.com/vllm-project/vllm/pull/30412) — Skip lm_head mapping for models with tied word embeddings.
GGUF loading failed with `RuntimeError: Failed to map GGUF parameters: ['lm_head.weight']` for models like Gemma2 that share weights between input embeddings and output projection. Fix adds lm_head.weight to sideload params when `tie_word_embeddings=True`.

3. [#30702](https://github.com/vllm-project/vllm/pull/30702) — Handle missing config.json in speculator probe for GGUF models.
The speculator probe tried to load config.json before GGUF handling ran, failing at engine init. More targeted fix following reviewer feedback that Transformers already handles GGUF config extraction.

4. [#33846](https://github.com/vllm-project/vllm/pull/33846) — Reduce Triton TILE_SIZE on Blackwell for large head_size with float32.
Blackwell (SM 120) has a 101KB shared memory limit per block. Triton's default TILE_SIZE=32 with `head_size=256` and float32 needs ~117KB, crashing with `OutOfResources` on first inference. Fix detects Blackwell + float32 + head_size=256 and drops TILE_SIZE to 16 (~66KB), unblocking Gemma2/Gemma3 GGUF inference on RTX 5090 at 373 tok/s.

5. [#37220](https://github.com/vllm-project/vllm/pull/37220) — Consolidate Gemma2/3 GGUF fixes for correctness on Blackwell.
Single PR consolidating four related GGUF fixes per reviewer request: embedding `quant_config` so `GGUFEmbeddingMethod` is selected, EOS token extraction from GGUF metadata for HF blob paths, skipping missing parameters during weight loading, and selecting plain `RMSNorm` instead of `GemmaRMSNorm` for GGUF (llama.cpp bakes +1 into the weights, so `GemmaRMSNorm`'s own +1 caused double addition → gibberish). Validated on RTX 5090: 43.9% HumanEval, 66.5% IFEval on gemma-2-2b GGUF.

</details>

**[Hugging Face Transformers](https://github.com/huggingface/transformers):** While debugging Gemma2/Gemma3 GGUF output quality in vLLM, I traced the root cause upstream — Transformers' GGUF loader wasn't mapping `attn_logit_softcapping` from GGUF metadata into the HuggingFace config, causing models to silently use the wrong default. [#42881](https://github.com/huggingface/transformers/pull/42881) adds the config mappings for both architectures.

## Tech Stack

<p>
  <img src="https://skillicons.dev/icons?i=python,cpp,pytorch,fastapi,linux,git,github" />
  <br>
  <img src="https://img.shields.io/badge/CUDA-76B900?style=for-the-badge&logo=nvidia&logoColor=fff" alt="CUDA" />
  <img src="https://img.shields.io/badge/Claude-191919?style=for-the-badge&logo=claude&logoColor=fff" alt="Claude" />
  <img src="https://img.shields.io/badge/vLLM-0D96F6?style=for-the-badge" alt="vLLM" />
  <img src="https://img.shields.io/badge/Transformers-FFD21E?style=for-the-badge&logo=huggingface&logoColor=000" alt="Transformers" />
</p>

## GitHub Stats

<p>
  <img src="https://github-readme-stats.vercel.app/api?username=kitaekatt&theme=transparent&show_icons=true&hide_border=true&count_private=true" />
</p>

## Connect

- **LinkedIn:** [therealchristina](https://www.linkedin.com/in/therealchristina/)
- **X/Twitter:** [@truffle](https://x.com/truffle)
- **Location:** Austin, Texas

---

<sub>Claude · AI/ML · LLM Inference · League of Legends · Mass Effect · Wild Rift · University of Waterloo</sub>
