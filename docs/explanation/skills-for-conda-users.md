# Skills for conda users

You already know how conda installs packages into environments. Here is how that fits with AI coding agents and skills. This page explains the pieces. The {doc}`../tutorials/skill-forge` tutorial walks through using them.

## An agent is a program you work with

An AI coding agent is an application, such as Claude Code, that uses a language model to help carry out tasks. Depending on the application and the permissions you give it, it can read project files, suggest or make edits, and run commands. You might ask it to investigate a failing test or help write a data-processing script.

You install and configure the agent separately. Conda-skills does not supply an AI model, start an agent, or grant it permission to run anything.

## A skill is a reusable set of instructions

Instead of explaining the same project conventions or library practices in every conversation, you can put them in a skill. The agent can read those instructions when working on a relevant task. Exactly when it loads them depends on the agent.

A skill is a folder, usually containing just `SKILL.md` to start with. It can also include supporting files:

```text
review-notes/
  SKILL.md                 # name, description, and instructions
  references/checklist.md  # optional background material
  scripts/check-notes.py   # optional code the agent might run
```

For example, `SKILL.md` could contain:

```markdown
---
name: review-notes
description: Summarize code-review findings supplied by the user.
---

For each finding, keep its file location, the problem, and the proposed fix.
Say when information is missing. Do not invent findings.
```

The header tells the agent what the skill is for. The body tells it how to approach the task. The [Agent Skills specification](https://agentskills.io/specification) defines this format. These are instructions for a model to interpret, not a guarantee of correct results.

## Where conda fits

```{mermaid}
:alt: Conda installs skill files in an environment. After review, conda skill link creates a project link to those files. A compatible agent can read them through that link.
:align: center

flowchart TD
    package["Skill package"] -->|conda install| files["Skill files in a conda environment"]
    files -->|"Review, then conda skill link"| link["Project link to those files"]
    link -->|"Read by a compatible client"| agent["Your coding agent"]
```

Conda installs the files under `share/agent-skills/NAME/` and manages their package version and dependencies. After reviewing them, run `conda skill link NAME` from your project root. The link points to the installed directory without copying it. Your agent controls whether to load the instructions and which tools it may use.

By default, the link goes in `.agents/skills/` under the current directory. This is a shared directory convention, not a product named "Agents". The Claude-specific option uses `.claude/skills/`. Check which path your agent supports.

## The commands have separate jobs

| Command | Purpose |
|---|---|
| `conda install PACKAGE` | Install the package in an environment. |
| `conda skill list` | List packaged skills in the active/default environment. |
| `conda skill inspect NAME` | Show a skill's metadata and files before deciding to use it. |
| `conda skill open NAME` | Open its directory in your system file manager to review all its files. |
| `conda skill link NAME` | Make an installed skill available through a link in the current directory. |
| `conda skill status` | Inspect destination links, including broken ones. |
| `conda skill unlink NAME` | Remove the destination link, leaving the package alone. |
| `conda remove PACKAGE` | Uninstall the package, without cleaning up project links. |

`PACKAGE` and `NAME` may differ: `agent-skill-polars` supplies the skill `polars`. A skill about Polars does not necessarily install the Polars library. Only dependencies declared by its package affect conda's solver.

Install the plugin in the environment that runs conda, usually `base`. Your active environment can hold the skills. For another source, `list`, `inspect`, `open`, and `link` accept `-n` or `-p`. Destination commands such as `status` and `unlink` do not need that source selection. Home-directory changes require explicit `--global`.

## What you still need to decide

Read the instructions and supporting files before linking a skill. Use `inspect NAME --file SKILL.md` to read in the terminal, or `open NAME` to find the complete directory in your file manager. Opening the directory does not launch a packaged file or execute its instructions. On a machine without a graphical desktop, use `inspect`.

Package records and valid metadata do not make a skill's advice trustworthy. Keep the agent's permissions appropriate for your project, especially when a skill includes scripts.

Links expose the installed files directly. Updating a package changes what linked projects can read, and uninstalling it leaves broken links. An agent may also retain instructions it has already loaded. Review updates and follow your agent's reload instructions.

This approach is useful when you want versioned skills or the same package selection across projects. A single skill you maintain locally may need no package at all. Conda-workspaces is optional for sharing environments, not a prerequisite for using a skill.

```{button-ref} ../tutorials/skill-forge
:color: primary

Try one skill
```

Or browse the {doc}`../demos` first. The {doc}`agent-discovery` explanation covers source and destination details, and {doc}`../reference/skill-format` lists the exact package requirements. The packaging approach comes from Pavel Zwerschke's pixi-skills and skill-forge work, described in {doc}`prior-art`.
