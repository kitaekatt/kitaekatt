# Christina Norman
**Agentic Systems Engineer/Designer**

> For 20 years I've designed, built, and scaled world-class games like League of Legends and Mass Effect, driving the creation of systems that deliver joy to players and generate billions of dollars in incremental revenue. Now I'm seeking to deliver a greater impact by designing and building frontier AI-powered systems.

### Impact
- 🎮 **Ported League of Legends to mobile (Wild Rift)** → **$1B+** incremental revenue
- 📈 **Rebuilt League's engagement, retention & monetization** → **billions** more in incremental revenue
- 🚀 **Co-founded Elodie Games** — raised **$39M**, ~**$80M** valuation, ~**60** people at peak
- 🗣️ **Built Mass Effect's conversation system** — now the industry standard for interactive dialogue

## What I'm Building
Claude code plugins focused on managing enterprise claude repos, and enhancing claude's ability to act as a perforce and unreal developer.
 **[plugins-kit](https://github.com/kitaekatt/plugins-kit)** — [docs](https://kitaekatt.github.io/plugins-kit/) · [architecture](https://deepwiki.com/kitaekatt/plugins-kit/)

- **bootstrap** — a dependency/provisioning engine every plugin rides on: declare your tools, venvs, git dependencies, marketplaces, and per-user config in a `bootstrap.json`, and bootstrap brings the environment into that state automatically at session start.
- **p4-kit** — a Perforce-based code reviewer (multi-agent review of pending changelists).
- **unreal-kit** — skills and tools that let Claude function as an Unreal developer.

## What I've Built
- **LLM-driven character conversation** — the Mass Effect conversation system, directed by LLMs. *(Case study coming.)*
- **Localization pipeline** — an iterative AI system that keeps refining each translation until the options are exhausted, turning an LLM's tireless workhorse capacity into measurably higher translation quality.
- **Local LLM Manager** — a platform for running and benchmarking LLMs and diffusion models locally: automatic backend selection (vLLM/CUDA, Apple Metal, CPU), server/client serving, and full model lifecycle management.
- **vLLM & HuggingFace Transformers fixes** — merged GGUF-backend fixes for quantized models on Blackwell (RTX 5090): multi-process hangs, dtype conflicts, weight loading, plus an upstream Transformers config-mapping fix. [vLLM PRs](https://github.com/vllm-project/vllm/pulls?q=author%3Akitaekatt) · [Transformers #42881](https://github.com/huggingface/transformers/pull/42881)

## Selected Experience
- **BioWare** — *Lead Programmer* (built Mass Effect's conversation system) → *Lead Gameplay Designer* (ME2/ME3 core gameplay & co-op multiplayer).
- **Riot Games** — Design leadership across League of Legends & Wild Rift (*Lead Designer → Project Lead → Design Director*).
- **Elodie Games** — *President & Co-Founder*.
- B.Math, Honours Computer Science — University of Waterloo.

## Open Source & Writing
- **Claude Code** — filed feature requests & bug reports that shipped as real fixes (per-terminal session affinity for `--continue`, silent plugin-skill registration failures, PreToolUse hooks dropping AskUserQuestion answers).
- **Writing:** [Mastering Cache Hits in Claude Code](https://dev.to/kitaekatt/mastering-cache-hits-in-claude-code-5648) · more on [dev.to](https://dev.to/kitaekatt)

## Connect
- **LinkedIn:** [therealchristina](https://www.linkedin.com/in/therealchristina/) · **X:** [@truffle](https://x.com/truffle) · **Location:** Austin, Texas
