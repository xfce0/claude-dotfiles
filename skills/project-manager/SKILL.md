---
name: project-manager
description: Create and manage projects in the Obsidian vault. Creates structured project folders (overview, conversation log, links, documents), ingests local files and URLs, maintains a projects dashboard (.base), and queries project context. Use when the user wants to create a new project, add data to a project, check project status, or manage project notes.
---

# project-manager

Manage projects inside an Obsidian vault with structured folders, automatic summarization, and a central dashboard.

## Triggers

Use this skill when the user says any of:
- "create project", "new project", "onboard project"
- "add to project", "ingest into project", "update project"
- "project status", "what's happening with project X"
- "list projects", "show projects dashboard"

## Project Structure

Every project lives in `projects/<project-name>/`:

```
projects/
├── projects.base              # dashboard: all projects as a table
└── <project-name>/
    ├── overview.md            # project profile, scope, contacts, tech stack
    ├── conversation-log.md    # chronological history of events and decisions
    ├── links.md               # external references (URLs, docs, repos)
    └── documents/             # static files (contracts, NDAs, proposals, PDFs)
```

## Commands

### 1. Create Project

**Trigger:** User wants to start a new project.

**Steps:**

1. Ask the user for the project name (if not provided in the argument)
2. Check if `projects/` folder exists; create if not
3. Create the project folder and all files using the templates below
4. Update `projects/projects.base` to include the new project
5. Report what was created

**Ask the user:**

```
What's the project name?
```

Then optionally:

```
Tell me about this project (or skip and fill in later):
- What is it about?
- Who is the client/stakeholder?
- What's the tech stack or domain?
- Any deadlines?
```

**Create `projects/<name>/overview.md`:**

```markdown
---
type: project
title: <Project Name>
status: active
client:
started: <DD/MM/YYYY>
tags:
  - project
---

# <Project Name>

## Profile

| Field | Value |
|-------|-------|
| Client | |
| Status | Active |
| Started | <today> |
| Domain | |

## Scope

### Phase 1


## Tech Stack

-

## Contacts

| Name | Role | Email |
|------|------|-------|

## Notes

```

**Create `projects/<name>/conversation-log.md`:**

```markdown
---
type: log
project: "[[<Project Name>]]"
---

# Conversation Log — <Project Name>

> Chronological record of all communications, decisions, and events.

## <DD/MM/YYYY> — Project Created

- Project initialized in vault
```

**Create `projects/<name>/links.md`:**

```markdown
---
type: links
project: "[[<Project Name>]]"
---

# Links — <Project Name>

## Repositories


## Documentation


## External Resources

```

**Create `projects/<name>/documents/` folder** (empty, for static files).

**Update `projects/projects.base`:**

If `projects/projects.base` does not exist, create it:

```json
{
  "headings": {
    "Project": { "type": "file" },
    "Status": { "type": "string" },
    "Client": { "type": "string" },
    "Started": { "type": "date" },
    "Last Updated": { "type": "date" }
  },
  "rows": [],
  "views": [
    {
      "name": "All Projects",
      "type": "table",
      "config": {
        "filter": [],
        "sort": [{ "column": "Last Updated", "direction": "desc" }],
        "columns": ["Project", "Status", "Client", "Started", "Last Updated"]
      }
    }
  ]
}
```

If it exists, read it and append the new project row.

### 2. Ingest Data into Project

**Trigger:** User wants to add files, URLs, or text to an existing project.

**Steps:**

1. Identify the target project (ask if ambiguous, list existing projects)
2. Determine the data source type:

| Source | Detection | Action |
|--------|-----------|--------|
| Local folder/files | Path to directory or files | Read each file, summarize, route to correct location |
| URL (article) | `http://` or `https://` (not YouTube) | Use `defuddle parse <url> --md` or WebFetch, summarize |
| YouTube URL | `youtube.com` or `youtu.be` | Extract transcript via youtube-transcript-api, summarize |
| Pasted text | Plain text in the message | Summarize and route |
| PDF file | `.pdf` path | Read with Read tool, summarize |

3. For each piece of content, classify it:

| Type | Destination | Action |
|------|-------------|--------|
| **Static document** (contract, NDA, proposal, agreement) | `documents/` | Copy file as-is, add reference to links.md |
| **Conversation** (email thread, meeting notes, chat log) | `conversation-log.md` | Summarize in chronological order, append to log |
| **Reference** (article, tutorial, documentation) | `links.md` | Add URL with description |
| **Key details** (scope, contacts, tech decisions) | `overview.md` | Update relevant section |

4. After processing, auto-extract and update:
   - Wikilinks to related vault notes (search for matching topics)
   - Tags in overview.md frontmatter
   - Contacts table if names/emails found
   - Update `Last Updated` in projects.base

5. Generate a summary report:

```
## Import Summary

**Project:** <name>
**Files processed:** N
**Added to:**
- conversation-log.md: N entries
- documents/: N files
- links.md: N references
- overview.md: updated scope, contacts

**Key takeaways:**
- <takeaway 1>
- <takeaway 2>
```

### 3. Query Project Status

**Trigger:** User asks about a project's status, action items, or context.

**Steps:**

1. Read the project's `overview.md` and `conversation-log.md`
2. Summarize: current status, recent events, pending action items
3. If the user asks to draft a response or email, use project context to generate it

### 4. List All Projects

**Trigger:** User asks to see all projects or the dashboard.

**Steps:**

1. Read `projects/projects.base`
2. Also scan `projects/*/overview.md` for up-to-date status
3. Present a summary table

### 5. Update Project

**Trigger:** User wants to change status, add notes, log a decision, or update scope.

**Steps:**

1. Identify the project and what to update
2. Edit the relevant file (overview.md for scope/status, conversation-log.md for events)
3. Update `projects.base` if status changed
4. Confirm the change

## Rules

- All project notes use **wikilinks** for internal references
- Write summaries in the **same language as the source data**
- Never overwrite existing content — always **append** to conversation-log.md
- Static documents go to `documents/` as-is — do NOT summarize contracts/NDAs/agreements
- Keep overview.md concise — it's a reference card, not a full report
- Always update `Last Updated` in projects.base after any change
- When ingesting, check for **duplicates** before adding (compare titles/dates in conversation-log)
- Use the `obsidian:obsidian-markdown` skill conventions for all created files
- Use the `obsidian:obsidian-bases` skill conventions for .base files
