# Book Marginalia Agent

Turn a highlighted passage into a thought worth keeping.

Book Marginalia Agent is an open [Agent Skill](https://github.com/openai/skills) for personal, critical reading notes. It can explain what an author means, connect the passage to the current reader's own opt-in notes, challenge weak assumptions, and turn a day of highlights into a reading journal.

If another AI already knows the reader well, the reader can bring over a short, reviewed context packet without sharing credentials or a complete chat archive.

The method is shared. The reader data is not.

## Why

Most highlight tools preserve text. Most AI summaries flatten it. This project focuses on the missing step between them: helping a reader form a precise response to one passage.

The default marginal note contains:

- **Meaning** — a faithful restatement of the author's claim.
- **Personal connection** — a link to this reader's verified local context, with its source.
- **Challenge** — a boundary, counterexample, structural cause, or missing premise.
- **Takeaway** — one useful question, observation, or small experiment.

It avoids generic praise, invented memories, and the habit of turning every paragraph into productivity advice.

## What works today

- “Just this passage” / “就这句” balanced marginalia.
- Explain, connect, challenge, and apply modes.
- Experimental Apple Books capture on macOS through Codex Desktop's Computer Use capability.
- Manual passage input for any reader or platform.
- A private, per-reader local vault.
- A provider-neutral import flow for reader-approved context from any long-used AI.
- Explicit save and daily reading-note workflows.
- A dependency-free Python helper for safe vault initialization and append-only capture.

Apple Books capture is intentionally labelled experimental: the agent can inspect visible page context and highlights, but Apple Books does not expose a general public API for its complete highlight database. Manual text input remains the reliable fallback.

## Privacy model

The public repository contains only the reading method, schemas, helper code, and invented test data.

Each reader has a separate local vault:

```text
BookMarginalia/
├── profile.md       # facts the reader explicitly provided
├── memories/        # opt-in personal notes
│   └── imports/     # reader-approved context packets from any AI
├── highlights/      # saved passages and marginalia
└── daily/           # generated reading journals
```

The agent must:

- use only verified reader context;
- show which memory source informed a personal connection;
- say when no relevant memory was found;
- keep agent interpretation separate from the reader's own words;
- never save a passage or personal fact without an explicit request or enabled capture setting;
- never place a reader vault inside this repository.

## Bring context from the AI that already knows you

Say:

```text
Use $book-marginalia-agent. Help me import my reader context from the AI I already use.
```

The agent gives you a provider-neutral export prompt. Use it with ChatGPT, Claude, Gemini, Copilot, a local model, or another assistant. The returned Markdown remains a draft until you review it and say `确认导入`.

This is intentionally not automatic memory sync. The agent does not ask for account credentials, API keys, or a raw archive of private conversations. The complete workflow and export prompt live in [`references/context-import.md`](skills/book-marginalia-agent/references/context-import.md).

## Install in Codex

Clone the repository and copy the skill into your personal skills directory:

```bash
git clone https://github.com/dudu913019449-creator/book-marginalia-agent.git
cp -R book-marginalia-agent/skills/book-marginalia-agent ~/.codex/skills/
```

The skill becomes available in a new Codex turn as `$book-marginalia-agent`.

## Try it

Highlight a passage in Apple Books on macOS, then say:

```text
Use $book-marginalia-agent. 就这句。
```

Other useful requests:

```text
说人话。
联系我，但没有相关记忆就直说。
反驳一下。
这句话怎么用？
存一下。
生成今日札记。
```

Without Apple Books integration, paste a passage directly:

```text
Use $book-marginalia-agent on this passage:
“An invented example passage goes here.”
```

## Local vault helper

The helper uses only the Python standard library.

Initialize a vault:

```bash
python3 skills/book-marginalia-agent/scripts/vault.py init \
  --vault ~/Documents/BookMarginalia
```

Append a structured JSON entry:

```bash
python3 skills/book-marginalia-agent/scripts/vault.py add \
  --vault ~/Documents/BookMarginalia \
  --entry /path/to/entry.json
```

Read one day's saved entries for synthesis:

```bash
python3 skills/book-marginalia-agent/scripts/vault.py list-day \
  --vault ~/Documents/BookMarginalia \
  --date 2026-08-28
```

After reviewing a context packet, import it with an explicit confirmation flag:

```bash
python3 skills/book-marginalia-agent/scripts/vault.py import-context \
  --vault ~/Documents/BookMarginalia \
  --input /path/to/reader-context.md \
  --source "My long-used AI" \
  --date 2026-08-28 \
  --confirmed-by-reader
```

The JSON schema and Markdown format live in [`references/note-format.md`](skills/book-marginalia-agent/references/note-format.md).

## Project structure

```text
skills/book-marginalia-agent/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── note-format.md
│   ├── context-import.md
│   ├── personalization.md
│   └── quality-rubric.md
└── scripts/vault.py
```

## Test

```bash
python3 -m unittest discover -s tests -v
```

## Roadmap

- Improve selection detection across themes and highlight colors.
- Add importers for exported highlights without coupling the core skill to one service.
- Add an optional keyboard-shortcut or menu-bar shell around the agent.
- Evaluate saved-note rate and reader edits before building a full reading app.

## 中文简介

Book Marginalia Agent 是一个通用的读书边注 Agent：公共仓库只提供评论方法，每个使用者的背景、经历、旧笔记和划线都保存在自己的本地资料库中。

在 Mac 的 Apple Books 里划一句，然后说“就这句”，Agent 会生成：原意、与你有关、反面一问、带走什么。说“存一下”才会保存；说“今日札记”会把当天已保存的划线整理成读书笔记。

个性化不是把某个人写进提示词，而是运行时只检索当前使用者主动提供的资料。找不到相关经历时必须坦白，不能编造。

如果读者长期使用的 AI 已经更了解他，可以让那个 AI 生成一份简短的读者背景包。读者本人审核并说“确认导入”后，背景包才会保存到本地私人资料库；不需要交出账号、API Key 或完整聊天记录。

## License

[MIT](LICENSE)
