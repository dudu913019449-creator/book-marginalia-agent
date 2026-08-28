# Local note format

Use this reference when saving a marginal note or producing a daily synthesis.

## Storage rules

- Store personal data only in the reader's configured vault.
- Never store the full page or book when a selected passage is sufficient.
- Keep source text, agent interpretation, reader-authored text, and memory sources separate.
- Append rather than overwrite an existing daily highlight file.
- Use the reader's local date.

## Highlight entry

Save entries under `highlights/YYYY-MM-DD.md`:

```markdown
## HH:MM · Book title

- Chapter: Chapter title or unknown
- Location: Page, section, or unknown
- Mode: balanced
- Memory sources: profile.md; memories/2026-08-20-project.md

> The selected passage only.

### Agent marginalia

**原意：** ...

**与你有关：** ...

**反面一问：** ...

**带走什么：** ...

### Reader response

<!-- Keep the reader's own words or edits here. Leave blank until provided. -->
```

Use `Memory sources: none` when no personal context was used. Do not record a source merely because it was searched.

## Daily note

Save daily synthesis under `daily/YYYY-MM-DD.md`:

```markdown
# Reading note · YYYY-MM-DD

## Reading scope

## Recurring themes

## The highlight that mattered most

## Connections to my existing notes

## My emerging view

## Unresolved question

## Possible next step

## Source entries
- [[../highlights/YYYY-MM-DD]]
```

The “My emerging view” section must not present an agent-generated interpretation as the reader's belief. Use tentative wording unless the reader has edited or endorsed it.

## Optional helper

When `scripts/vault.py` is available:

```text
python3 scripts/vault.py init --vault /path/to/vault
python3 scripts/vault.py add --vault /path/to/vault --entry /path/to/entry.json
python3 scripts/vault.py list-day --vault /path/to/vault --date YYYY-MM-DD
```

The `add` entry JSON accepts:

```json
{
  "date": "2026-08-28",
  "time": "21:30",
  "book": "Book title",
  "chapter": "Chapter title",
  "location": "Page 27",
  "mode": "balanced",
  "quote": "Selected passage",
  "marginalia": {
    "meaning": "...",
    "connection": "...",
    "challenge": "...",
    "takeaway": "...",
    "short_note": "..."
  },
  "memory_sources": [],
  "reader_response": ""
}
```
