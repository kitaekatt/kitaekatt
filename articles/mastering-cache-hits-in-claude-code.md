---
title: Mastering Cache Hits in Claude Code
description: Understanding how caching works behind the scenes so you can reduce costs and get faster responses — even though you never touch the API directly.
tags: [claudecode, ai, llm, productivity]
canonical_url: https://x.com/truffle/status/2024254523175481849
published: false
---

Understanding how caching works behind the scenes so you can reduce costs and get faster responses — even though you never touch the API directly.

## Table of Contents

1. [What Are Cache Hits and Why Should I Care?](#what-are-cache-hits-and-why-should-i-care)
2. [Anatomy of an API Call](#anatomy-of-an-api-call)
3. [Cache Hits and Misses Explained](#cache-hits-and-misses-explained)
4. [What Breaks the Cache](#what-breaks-the-cache)
5. [Cache Lifetime and the TTL Timer](#cache-lifetime-and-the-ttl-timer)
6. [Structuring Your Work for Better Caching](#structuring-your-work-for-better-caching)
7. [Caching Anti-Patterns](#caching-anti-patterns)
8. [API-Level Details (For When You Need Them)](#api-level-details-for-when-you-need-them)
9. [References](#references)

---

## What Are Cache Hits and Why Should I Care?

Every time Claude Code sends a message on your behalf, it makes an API call to Anthropic. That API call includes everything Claude needs to respond: the system prompt, any tool definitions, your `CLAUDE.md` files, and your entire conversation history. On a long session with a big codebase loaded, this can easily be 50,000–200,000+ tokens of input.

Without caching, Anthropic's servers have to fully process all of those tokens from scratch on every single message — even though 99% of them are identical to what was sent 30 seconds ago. That's expensive and slow.

### What caching does

Caching saves the computational work that the server already did on the unchanged portion of your input. Think of it like this:

- **Without caching**: You send a 100-page document plus a question. The server reads the entire 100 pages, then answers your question. You send a different question about the same document. The server reads the entire 100 pages again, then answers. Every question costs the same.
- **With caching**: You send a 100-page document plus a question. The server reads the 100 pages, saves its understanding of them, then answers. You send a different question. The server loads its saved understanding of the 100 pages (fast and cheap), then only processes your new question. Every follow-up question is dramatically faster and cheaper.

### What it costs

The token costs below are API prices, but they're directly analogous to how your Claude plan's usage limit is consumed. Cache hits use less of your usage allowance than cache misses. Optimizing your cache hit rate stretches your plan further.

Using Claude Sonnet 4.5 as an example:

| What you're paying for | Cost per million tokens | Relative to base |
|---|---|---|
| Regular input tokens (no caching) | $3.00 | 1x |
| Cache write (5-min TTL) | $3.75 | 1.25x |
| Cache write (1-hour TTL) | $6.00 | 2x |
| Cache read (hitting the cache) | $0.30 | 0.1x |
| Output tokens | $15.00 | (not affected by caching) |

The key number: **a cache hit is 10x cheaper than uncached input.** It's also 12.5x cheaper than a cache write on the 5-minute TTL, or 20x cheaper than a 1-hour TTL write. You break even after just 2 messages — message 1 costs $0.375 on 100K tokens (the cache write), message 2 costs $0.03 (the cache read), for a cumulative $0.405. Without caching, those same 2 messages would cost 2 × $0.30 = $0.60. After that, every additional message saves ~$0.27 on a 100K-token context.

Over a full 20-turn session with 100K tokens of stable context:

- **Without caching**: 20 × $0.30 = **$6.00** in input costs
- **With caching**: $0.375 (first write) + 19 × $0.03 = **$0.945** in input costs
- **Savings: 84%**

Cached tokens are also served significantly faster — latency on time-to-first-token improves substantially, though the exact improvement varies by platform and workload. Some platforms have reported up to 85% TTFT reduction in optimal conditions.

As a Claude Code user, you don't directly control caching — Claude Code handles the API calls for you and automatically places cache breakpoints on your behalf. But understanding how caching works lets you structure your projects and conversations in ways that naturally lead to more cache hits, lower costs, and snappier responses.

> **Note on model support:** Prompt caching is generally available on Claude Opus 4.5, Opus 4.1, Opus 4, Sonnet 4.5, Sonnet 4, Haiku 4.5, Haiku 3.5, and Haiku 3. It's also supported on Opus 4.6 and Sonnet 4.6 — the official documentation hasn't been updated to reflect this yet.

> **Caches are isolated per model.** Switching models mid-session (e.g. via `/model`) means a full cache miss. You cannot build a cache with a cheaper model and read it with a more expensive one.

### Cache hit rate

```
cache_hit_rate = cache_read_tokens / (cache_read_tokens + cache_write_tokens + input_tokens)
```

A well-cached active session should have a hit rate around 90%.

### cache-kit plugin

Understanding cache performance isn't easy out of the box — Claude Code doesn't surface cache hit rates or token breakdowns anywhere in its UI. I built a plugin to fix that. The cache-kit plugin for Claude Code provides a `/cache-report` skill that reads your local session transcripts and generates a formatted cache performance summary: hit rate, token breakdown by TTL, and per-request stats.

**Marketplace:** `git@github.com:kitaekatt/plugins-kit.git`
**Plugin name:** `cache-kit`

![cache-kit /cache-report output showing 89% hit rate on a 112-request session](https://raw.githubusercontent.com/kitaekatt/kitaekatt/main/articles/images/cache-report-screenshot.png)

---

## Anatomy of an API Call

To understand caching, it helps to know what Claude Code actually sends to the API on your behalf. Every API call has these parts, assembled in this order:

1. **Tool definitions**
   All the tools Claude Code can use (bash, file edit, search, etc.)
   These are the same on every call within a session.

2. **System prompt**
   Claude Code's instructions, your `CLAUDE.md` content, project context.
   This is mostly the same on every call within a session.

3. **Messages (your conversation)**
   Every user message and assistant response in the current session, in chronological order. This grows by ~2 messages each turn (your new message + Claude's response from last turn).

Caching works on this content **from the top down**. The server looks at the input starting from the tool definitions and moving forward, and checks how far it can go before it hits something that's different from what it cached last time.

The portion that matches the cache is called the **cached prefix** — "prefix" just means "the beginning part." Everything from the start of the input up to the point where something changed gets served from cache. Everything after that point gets processed fresh.

### How Claude Code places cache breakpoints

Claude Code automatically places `cache_control` breakpoints on the last content block of user and assistant messages. Thinking blocks are explicitly excluded from cache breakpoints. This is all automatic — no user configuration needed or possible (aside from disabling caching entirely via environment variables).

---

## Cache Hits and Misses Explained

This is the core concept, so let's walk through a concrete example.

**Example: A 5-turn Claude Code session**

Imagine you're working in Claude Code on a project. Your session has tool definitions (~5K tokens), a system prompt with `CLAUDE.md` (~3K tokens), and you're going back and forth with Claude.

**Turn 1 — You ask your first question**

What's sent to the API:
```
[Tools: 5K tokens] [System: 3K tokens] [Your message: 50 tokens]
```

Cache result:
- Cache miss (nothing cached yet)
- → Server processes all 8,050 tokens fresh
- → Saves the processed result to cache for next time

**Turn 2 — You ask a follow-up question**

What's sent to the API:
```
[Tools: 5K] [System: 3K] [Turn 1 Q: 50] [Turn 1 Answer: 500] [Your new Q: 60]
```

Cache result:
- Cache HIT on [Tools + System + Turn 1 Q] = 8,050 tokens
- Cache miss on [Turn 1 Answer + Your new Q] = 560 tokens
- → 93% of tokens served from cache

**Turn 3 — Another follow-up**

What's sent to the API:
```
[Tools: 5K] [System: 3K] [Turn 1 Q+A] [Turn 2 Q+A] [Your new Q: 45]
```

Cache result:
- Cache HIT on [Tools + System + Turn 1 + Turn 2 Q] = ~8,660 tokens
- Cache miss on [Turn 2 Answer + Your new Q] = ~545 tokens
- → 94% of tokens served from cache

By turn 5, you might have 95%+ of tokens served from cache. By turn 20 with a large codebase loaded, it could be 50K+ tokens of cached history and only a few hundred tokens of new content per turn.

### The key insight

**You don't get 100% cache hits or 100% cache misses on a message.** Each message is a mix. The unchanged beginning of the conversation is a cache hit. The new content at the end is a cache miss. As your conversation grows, the ratio of cached-to-fresh tokens improves dramatically.

### Why the "prefix" concept matters

Caching only works on the **beginning** of the input, moving forward. It can't skip over a changed section and cache something after it. If you imagine the input as a timeline:

```
[cached   ] [cached   ] [cached   ] [CHANGED  ] [not cached  ] [not cached  ]
                                         ↑
                                  Cache stops here.
                            Everything after this is processed fresh,
                            even if it's identical to last time.
```

In normal Claude Code usage, the prefix grows cleanly — each turn appends new content at the end, and everything before it stays cached. The prefix only breaks mid-conversation if you do something that alters earlier content, like using `/rewind` (which removes messages from the history) or toggling a feature flag (which changes the system prompt). These are the situations where understanding prefix matching helps you diagnose unexpected cache misses.

---

## What Breaks the Cache

The cache requires **exact byte-for-byte matching** from the beginning of the input forward. Anything that changes the content — even in ways that seem trivial — breaks the cache from that point onward.

### Things that invalidate the cache

In the context of Claude Code, the most common cache-breakers are:

**Session-level changes:**
- Starting a new conversation (no cache carries over between sessions)
- Resuming a session (`--continue`, `--resume`, `--fork-session`) — the system prompt is regenerated, tool definitions are reassembled, and the cache TTL has almost certainly expired while you were away. In theory, if you resumed within the TTL window (e.g. you accidentally closed a terminal and immediately reopened), you could get a cache hit since the prefix is identical — but in practice this rarely happens.
- Being idle longer than the cache retention period (5 minutes for Pro/API, 1 hour for Max)

**Content changes that cascade:**
- Toggling features like web search or extended thinking on/off
- Switching models via `/model` (caches are per-model)
- Toggling fast mode (changes the model configuration)
- Using `/rewind` (see [Caching Anti-Patterns](#caching-anti-patterns))

### The invalidation hierarchy

Changes cascade downward through this structure:

```
Tool definitions  →  If these change, EVERYTHING below loses its cache
       ↓
System prompt     →  If this changes, all messages lose their cache
       ↓
Messages          →  Changes here only affect messages from the change onward
```

In a normal active Claude Code session, tool definitions and the system prompt don't change between turns — they're assembled once at session start. This means the cache stays valid and you get consistent cache hits on the entire prefix up to your latest new content. The invalidation hierarchy only matters if you change your `CLAUDE.md`, system prompt, or tools and then restart — at which point the system prompt is regenerated, tool definitions are reassembled, and the cache is cold.

![Cache invalidation matrix showing which changes break the tools, system, and messages cache layers](https://raw.githubusercontent.com/kitaekatt/kitaekatt/main/articles/images/cache-table.jpg)

### Things that don't break the cache

- Adding a new message at the end of the conversation (the prefix is preserved)
- Changing only your latest question (the prefix up to the new content is preserved)
- Claude giving a different-length response (output is never cached, only input)

---

## Cache Lifetime and the TTL Timer

### How the timer works

Cached content expires after a set period of inactivity. Every time a cache hit occurs, the timer resets. So as long as you're actively working, your cache stays warm.

**The key word is "inactivity."** If you send a message at 2:00, another at 2:03, and another at 2:07 — the cache stays warm the whole time because each hit resets the clock. But if you send a message at 2:00 and then nothing until the TTL expires — the cache is gone and your next message rebuilds it from scratch.

### Which TTL you get

**Max plan subscribers get 1-hour TTL.** This is based on Claude Code source code inspection as of February 2026 — the `P31` function grants 1h TTL to Max subscribers (not on overage), controlled by a server-side feature flag (`tengu_prompt_cache_1h_config`). All cache writes use the 1h TTL automatically. Note that this is an implementation detail that could change without notice.

**Pro plan and API-key users get 5-minute TTL.** This is the default, and it means you need to stay more active to keep the cache warm.

### Why the TTL matters: a cost example

Consider a session with 100K tokens of cached context:

**Example 1** — You take 6 minutes to compose a thoughtful message (Pro plan, 5-minute TTL):
- Cache has expired. Your message triggers a full cache rebuild.
- Cost on the cached content: **1.25x** (cache write)

**Example 2** — After 3 minutes you send "do nothing, just keeping cache warm", then 3 minutes later send your real message:
- The keepalive message hits the cache (0.1x) and resets the timer.
- Your real message also hits the cache (0.1x).
- Cost on the cached content: **0.2x** (two cache reads)
- Plus a small output cost for the throwaway response.

Example 2 is about **6x cheaper** on the cached content, even accounting for the throwaway message. But it's a clunky user experience — and it illustrates exactly why the 1-hour TTL on Max plans is valuable. Max users don't need keepalive hacks; they have a full hour of breathing room.

### Practical tips

- **Max users**: You have a 1-hour window. Take your time composing messages, reviewing output, or stepping away briefly. Your cache will be there when you get back.
- **Pro/API users**: Stay within the 5-minute window during active work. If you know you'll be away longer, accept that the next message will rebuild the cache (slightly slower and more expensive), then caching resumes normally.

---

## Structuring Your Work for Better Caching

Now that you understand what the cache is, how it expires, and what breaks it, here are the habits that keep your cache hit rate high.

### Batch related work into one session

If you know your work is going to involve reading significant data into context, it's better to have one longer conversation about that data than many small conversations where you re-read the same data each time. Loading the same context once and asking multiple questions is dramatically cheaper than loading it separately.

**Loading a 100K-token file and asking 5 questions in one session:**
- Turn 1: 100K cache write (1.25x) + question
- Turns 2–5: 100K cache read (0.1x) each + question
- Total file cost: 1.25x + 4 × 0.1x = **1.65x**

**Loading the same file in 5 separate sessions, 1 question each:**
- Each session: 100K cache write (1.25x) + question, cache never reused
- Total file cost: 5 × 1.25x = **6.25x**

The five-session approach is **~3.8x more expensive** on the file alone, because you pay the cache write cost every time and never get a cache hit. The cache you built in each session is thrown away unused.

### Fork sessions for parallel work

Claude Code's `--fork-session` feature lets you create multiple independent sessions that all share the same conversation history up to the fork point. Because the forked sessions share an identical prefix, they all benefit from the same cache.

The workflow: build a base session with shared context (load files, establish the problem), then fork it into parallel investigations:

```bash
# Build a shared context session
claude
> Read src/db/queries.ts, src/api/routes.ts, src/middleware/auth.ts,
  src/services/payment.ts, and the last 200 lines of logs/production.log

# Name it, then fork into parallel investigations in separate terminals
/rename bug-investigation-base

# Terminal 1:
claude --resume bug-investigation-base --fork-session
> "Investigate the database timeout errors in the production logs."

# Terminal 2:
claude --resume bug-investigation-base --fork-session
> "Analyze whether token expiry handling could cause the 401 errors."

# Terminal 3:
claude --resume bug-investigation-base --fork-session
> "Check if the API route error handling is swallowing transaction failures."
```

The base session pays the cache write once. Each fork gets cache hits on the shared context: 1.25x + 3 × 0.1x = **1.55x** total. Three independent sessions each loading the same files would cost 3 × 1.25x = **3.75x** — about 2.4x more expensive and slower.

Each fork gets its own independent conversation history from the fork point onward. The base session remains unchanged and can be forked again. For clean separation between parallel workstreams, prefer `--fork-session` over resuming the same session in multiple terminals (which interleaves messages in the same session file).

---

## Caching Anti-Patterns

These are the things that silently destroy your cache or waste tokens. Avoid them when possible.

### Don't let the cache TTL expire during active work

The cache expires after a period of inactivity — 5 minutes for Pro/API users, 1 hour for Max users. Every time you let the timer expire, your next message pays the full cache write cost again. Keep the conversation moving during active work. If you're reviewing Claude's output and need more time, you're fine as long as you respond before the timer runs out.

### Don't preemptively load large context

There's no caching advantage to loading files early in a conversation "just in case." You pay the same cache write cost regardless of when you load them, and loading them early means you pay cache-read costs on those tokens for every remaining turn — even turns where the files are irrelevant to what you're asking about. Load context when you actually need it so you're not paying to re-cache tokens that aren't contributing to the current task.

### Don't switch models mid-session

Caches are isolated per model. If you switch from Sonnet to Opus via `/model` mid-session, the entire cache built on Sonnet is useless — Opus starts from a cold cache and pays the full write cost again. If you need to use a different model for a specific task, consider doing it in a separate session rather than switching back and forth within one session.

### Don't use /rewind

The `/rewind` command removes messages from the end of your conversation history. Even rewinding by a single turn changes the prefix — the cached version includes the message you just removed, but your new request doesn't. The server can't match the prefix it stored, so you get a cache miss on everything after the rewind point.

This matters most when you've built up significant context. If you loaded files, had a 30-turn conversation, and then rewind back to just after the file loads, you lose the cache on all 30 turns of conversation. Your next message rebuilds the cache from the file-load point forward. If you want to "start fresh" with the same loaded context, forking the session from the right point is far more cache-friendly than rewinding.

### Don't restart after CLAUDE.md or tool changes

Claude Code reads your `CLAUDE.md` files and assembles tool definitions at session start. If you edit `CLAUDE.md`, install a new MCP server, or add a plugin while a session is running, your current session is unaffected — it's still using the versions from when it started. It's tempting to restart immediately so Claude picks up the changes, but restarting means a full cache rebuild. If you're mid-flow on an expensive session with a lot of context loaded, the change can wait until you naturally finish the current task.

### Don't install MCP servers or plugins mid-session

Installing an MCP server or a plugin changes your tool definitions, which sit at the very top of the invalidation hierarchy — meaning everything below (system prompt and all messages) loses its cache on the next session start. This isn't a problem for your current session (it won't pick up the new tools until restart), but it means your next session will start with a cold cache that includes the new tool definitions. If you're planning to install several tools, batch them together so you only pay one cache rebuild rather than several.

---

## API-Level Details (For When You Need Them)

This section covers details that go beyond day-to-day Claude Code usage. It's here if you're building custom tooling, parsing session data, or just want to understand the internals.

### Environment variables for caching control

Claude Code's caching behavior is controlled entirely via environment variables — there are no settings.json options.

| Env Var | Effect |
|---|---|
| `DISABLE_PROMPT_CACHING` | Disable all caching |
| `DISABLE_PROMPT_CACHING_HAIKU` | Disable caching for Haiku model |
| `DISABLE_PROMPT_CACHING_SONNET` | Disable caching for Sonnet model |
| `DISABLE_PROMPT_CACHING_OPUS` | Disable caching for Opus model |
| `ENABLE_PROMPT_CACHING_1H_BEDROCK` | Enable 1h TTL on Bedrock |
| `CLAUDE_CODE_FORCE_GLOBAL_CACHE` | Force global system prompt caching |
| `ANTHROPIC_LOG=debug` | SDK debug logging (shows HTTP request/response details) |

### JSONL session transcripts

Every Claude Code session is stored as a JSONL file under `~/.claude/projects/<project>/`. Each assistant message entry contains a full usage object with cache metrics:

```json
{
  "input_tokens": 3,
  "cache_creation_input_tokens": 13099,
  "cache_read_input_tokens": 17976,
  "cache_creation": {
    "ephemeral_5m_input_tokens": 0,
    "ephemeral_1h_input_tokens": 13099
  },
  "output_tokens": 10
}
```

You can parse these files directly to build custom cache analytics. This is how the cache-kit plugin's `/cache-report` skill generates its reports — it reads the JSONL for the current session, aggregates the usage objects, and computes hit rates and token breakdowns.

### Extended thinking and caching

When Claude uses extended thinking in Claude Code, the thinking blocks appear in the conversation history sent on subsequent turns. These thinking blocks get cached automatically as part of the normal conversation prefix — they're treated like any other content in the message history.

The nuance is that thinking blocks are explicitly excluded from being *cache breakpoints* (the markers that tell the server "you can cache up to here"). This is handled automatically and doesn't affect your cache hit rate in practice. The thinking content still gets cached as part of the prefix when a later block has a breakpoint.

---

## Final Words

Cache hits aren't everything and there's nothing wrong with cache misses. Do whatever works for you.

---

## References

**Anthropic Official Documentation**

1. **[Prompt Caching — Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)** — The authoritative reference covering implementation, pricing, invalidation rules, and breakpoint strategy.

2. **[Prompt Caching with Claude — Anthropic Blog](https://www.anthropic.com/news/prompt-caching)** — The announcement post covering use cases, cost/latency benefits, and early customer results.

3. **[Prompt Caching Cookbook — Anthropic GitHub](https://github.com/anthropics/anthropic-cookbook/blob/main/misc/prompt_caching.ipynb)** — Jupyter notebook with hands-on examples comparing non-cached, cache-write, and cache-hit API calls with timing and cost analysis.

4. **[Token-Saving Updates on the Anthropic API — Anthropic Blog](https://www.anthropic.com/news/token-saving-updates)** — Covers cache-aware rate limits, simplified prompt caching, and token-efficient tool use.

5. **[Manage Costs Effectively — Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code/costs)** — Official guidance on Claude Code cost management, token optimization, and how Claude Code automatically applies prompt caching.

**Platform-Specific Guides**

1. **[Prompt Caching on Amazon Bedrock — AWS Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)** — Bedrock-specific implementation details, CloudWatch monitoring for cache metrics, and TTL behavior.

2. **[Effectively Use Prompt Caching on Amazon Bedrock — AWS Blog](https://aws.amazon.com/blogs/machine-learning/effectively-use-prompt-caching-on-amazon-bedrock/)** — Walkthrough of monitoring cache hit rates with CloudWatch dashboards and cost estimation.

3. **[Prompt Caching on Vertex AI — Google Cloud Documentation](https://docs.cloud.google.com/vertex-ai/generativeai/docs/partner-models/claude/prompt-caching)** — Google Cloud-specific caching behavior, TTL options, and pricing for Anthropic models on Vertex AI.

**Community Articles and Deep Dives**

1. **[Prompt Caching: The Secret to 60% Cost Reduction — Thomson Reuters Labs](https://medium.com/tr-labs-ml-engineering-blog/prompt-caching-the-secret-to-60-cost-reduction-in-llm-applications-6c792a0ac29b)** — Practical guide covering cache warming patterns, parallel request handling, and real-world cost analysis.

2. **[Prompt Caching: 10x Cheaper LLM Tokens, But How? — ngrok Blog](https://ngrok.com/blog/prompt-caching/)** — Technical deep-dive into what happens at the infrastructure level, with latency benchmarks comparing Anthropic and OpenAI caching.

3. **[Prompt Caching Guide 2025 — Prompt Builder](https://promptbuilder.cc/blog/prompt-caching-token-economics-2025)** — Cross-provider comparison of caching strategies across Anthropic, OpenAI, and Google.

4. **[Prompt Caching with OpenAI, Anthropic, and Google Models — PromptHub](https://www.prompthub.us/blog/prompt-caching-with-openai-anthropic-and-google-models)** — Side-by-side comparison of caching features, pricing, and best practices across major providers.

**Tools**

1. **cache-kit Plugin for Claude Code** — Provides `/cache-report` skill for viewing per-session cache performance stats directly in Claude Code. `git@github.com:kitaekatt/plugins-kit.git` (plugin: `cache-kit`)

---

*Last updated: February 2026. Pricing, model support, and feature details are subject to change — always verify against the [official Anthropic documentation](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching).*
