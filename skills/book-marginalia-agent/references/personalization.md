# Personalization and user isolation

Use this reference when creating a reader profile, connecting a passage to the reader, or deciding what personal context may be used.

## Principle

The public skill contains the method. Each reader owns a separate local vault containing their profile, memories, highlights, and daily notes. Never copy one reader's context into another reader's prompt, output, test fixture, or repository.

## Default vault

Resolve the vault in this order:

1. A path the user explicitly provides.
2. The `BOOK_MARGIN_VAULT` environment variable.
3. `~/Documents/BookMarginalia` after informing the user on first creation.

The optional helper initializes this layout:

```text
BookMarginalia/
├── profile.md
├── memories/
│   └── imports/     # reader-approved context packets from any AI
├── highlights/
└── daily/
```

Treat the entire vault as private. Do not place it under the skill directory. If the selected location is inside a Git repository, warn the user and add an ignore rule before saving personal content.

## Profile contents

Keep `profile.md` small and editable. Store only facts the reader explicitly supplied or confirmed:

```markdown
# Reader profile

## Current questions
- What am I trying to understand or change?

## Projects and responsibilities
- Facts the reader explicitly provided.

## Values and tensions
- Confirmed preferences, principles, or recurring conflicts.

## Commentary preferences
- Desired brevity, tone, and preferred modes.
```

Do not store speculative personality labels, diagnoses, sensitive traits, or inferred life events.

## Memory retrieval

Search in this order:

1. `profile.md` for stable, confirmed context.
2. Relevant reader-approved packets in `memories/imports/`.
3. Recent reader-authored notes in `memories/`.
4. Earlier saved highlights and the reader's own edits.
5. Explicit statements in the current conversation.

Prefer one strong connection over several weak ones. Cite the source compactly. A previous agent-generated comment is not evidence of the reader's belief unless the reader accepted, edited, or endorsed it.

An imported context packet is usable only when its header says `Status: reader-confirmed`. The reader's later correction overrides the imported packet. Read [context-import.md](context-import.md) when importing, reviewing, or resolving conflicts in context supplied by another AI.

## First use

Do not force an onboarding questionnaire before producing value. Generate a non-personal marginal note first. When personalization would materially improve it, invite the reader to provide one relevant piece of context, such as:

- “你最近正在做什么项目？”
- “这句话让你想到自己哪段经历？”
- “你更希望我解释、反驳，还是帮你应用？”

Save the answer only with the reader's permission.

If the reader says another AI already knows them, offer the portable context import instead of forcing a new questionnaire. Keep the first useful marginal note available even if the reader declines to import anything.

## Deletion and correction

When a reader corrects a profile fact, update the source rather than appending a contradictory duplicate. When they ask to forget something, remove the specified local entry and do not retain it in summaries or examples.
