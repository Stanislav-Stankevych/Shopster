# Triage & Project Workflow

This repository uses GitHub Issues + Project boards for planning. The goal is to keep the backlog transparent and make it easy to spot priorities.

## Labels

| Label | Use case |
| --- | --- |
| `bug` | A defect or regression. |
| `enhancement` | Feature request or improvement. |
| `chore` | Internal work (CI tweaks, docs, refactors). |
| `dependencies` | Dependabot/renovate updates. |
| `ci` | Continuous integration / deployment changes. |
| `good first issue` | Low-risk tasks, ideal for newcomers. |

Create labels via **Settings → Labels** or run:

```bash
gh label create bug --color "#d73a4a"
gh label create enhancement --color "#a2eeef"
gh label create chore --color "#fbca04"
gh label create dependencies --color "#0366d6"
gh label create ci --color "#0e8a16"
gh label create "good first issue" --color "#7057ff"
```

## Project board

Create a *V2* project named **Shopster Roadmap** with the following columns:

- **Backlog** — new issues, unprioritised.
- **In progress** — assigned items being worked on.
- **Review** — open PRs or issues pending validation.
- **Done** — merged / released.

Associate issues/PRs with the project to keep the roadmap up to date. Each item should have:

- linked PR (if applicable),
- clear acceptance criteria,
- labels from the table above.

## Definitions of done

- Code formatted (`task lint`, `pytest -m smoke`, `npm run build`).
- Documentation updated (README, docs/).
- CI pipeline green.
- Release notes entry (via Release Drafter).

Following this workflow keeps the repository pleasant for collaborators, reviewers, and hiring managers evaluating the project.
