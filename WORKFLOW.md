# DCG Development Workflow — Project Standard

This repository follows the Divine Creative Group One-Pager model, adapted to its existing architecture.

## Principles
- Inspect first; avoid asking the owner to repeat known information.
- Source of truth: GitHub repository + maintained project documentation.
- Prefer vanilla HTML/CSS/JavaScript, clean SEO, responsive accessible UI, minimal libraries.
- Preserve existing working frameworks where replacing them adds risk.
- Keep public pages fast; lazy-load heavy media and avoid unnecessary effects.
- Simple authentication and gated content only where needed; never ship secrets in frontend.
- Client-editable content should use a documented CMS/API boundary, not hardcoded production credentials.
- Build changes in coherent batches; validate before deployment.
- Never change production services or delete content without a backup, rollback plan, and explicit approval.

## Branch and release practice
- Stable branch: verify which branch corresponds to production before changing defaults.
- Feature work: dev/<project-or-release>.
- Review via pull request with screenshots, build result, API/playback smoke test, and rollback notes.
- Deploy preview first; production only after approval.

## Required project documents
- PROJECT.md: mission, status, decisions, next steps.
- ARCHITECTURE.md: stack, integrations, environments, deployment.
- WORKFLOW.md: development standards.
- CHANGELOG.md: user-visible milestones and technical changes.

## Multi-repository cleanup
Inventory first; identify deployed and actively maintained repositories.
Classify: active, legacy/reference, duplicate candidate, archive candidate.
Never delete, rename, archive, or overwrite repositories based only on matching names.
Prioritize the working DCG One-Pager repository as the reference implementation; document deviations per project.
