# System repo layout

Every system repo has this shape, so a developer who knows one knows all of them.

```
<system>/
  README.md  CLAUDE.md  AGENTS.md  LICENSE  CHANGELOG.md  SECURITY.md  CONTRIBUTING.md
  .env.example  .gitignore  .nvmrc  Makefile  docker-compose.yml
  apps/web      Next.js dashboard, built from the shared UI kit
  apps/api      FastAPI app (built with create_base_app) and the worker entry
  packages/     exact copy of the hub base, never edited here (core-py, ui-kit, ARCHITECTURE.md, BASE_MANIFEST.json)
  mock/         local mock vendor servers written from public docs
  data/         seed data and answer_key.json
  tools/        seed, scoring, doctor, check_env, check_base_copies
  docs/         numbered guides 00 to 15 and the reference docs
  prompts/      quick start prompts for Claude Code and Codex
  templates/    claude-code and codex
  deploy/       vercel, railway, hetzner, docker
  tests/        unit, integration, e2e, accessibility, visual
  .github/workflows/ci.yml
```

Numbered guides: 00 start here, 01 quick demo, 02 business basics check, 03 connect your tools, 04 environment variables, 05 run locally, 06 deploy to Vercel, 07 deploy to Railway, 08 deploy to Hetzner, 09 go live checklist, 10 using it for a client, 11 operating and backups, 12 updating, 13 security and data, 14 limits and honest notes, 15 troubleshooting.

Reference docs: ARCHITECTURE, CAPABILITIES, TOOLS-AND-ALTERNATIVES, DESIGN-NOTES, GLOSSARY, FACTS-AND-SOURCES.
