# Cryptorefills Skills — Agent Guide

Instructions:
- Be semantically dense and token efficient. Prefer concise, information-rich responses; avoid filler, repetition, and unnecessary elaboration.
- When editing, never mention the previous version or the changes you made. All contents must be authoritative and up to date.
- Abstract instructions that can be applied to multiple cases.
- Avoid creating new sections. Update existing knowledge instead.

This repository is a monorepo of agent skills for Cryptorefills, packaged as a **Claude Code / Cowork plugin marketplace**. Skills live in the `skills/` directory and are distributed through the plugin system shared by Claude Code and Claude Cowork.

## Installing the Plugin

### Claude Code

```shell
/plugin marketplace add cryptorefills/agents
/plugin install cryptorefills@cryptorefills-skills
```

### Claude Cowork

1. Open **Settings > Plugins**
2. Add the marketplace source `cryptorefills/agents`
3. Install the **cryptorefills** plugin

### npx

```shell
npx skills add cryptorefills/agents
```

### Local Testing

```shell
claude --plugin-dir ./
```

Once installed, Claude gains three skills:
- **cryptorefills-catalog** — search and explore 10,500+ gift cards, mobile top-ups, and eSIMs via MCP
- **cryptorefills-buy** — full MCP purchase workflow with guided elicitation and all crypto payment methods
- **cryptorefills-x402** — autonomous agent commerce with USDC on Base via x402 protocol (no account needed)

Skills activate automatically when Claude detects a relevant task.

## Country Code Formats

> **Important**: MCP skills (`cryptorefills-catalog`, `cryptorefills-buy`) use **uppercase** country codes (`US`, `IT`, `BR`). The x402 skill uses **lowercase** (`us`, `it`, `br`). Always match the case to the endpoint.

## Repository Structure

```
.claude-plugin/
  plugin.json          # Plugin manifest (name, version, author)
  marketplace.json     # Marketplace catalog listing the plugin
skills/
  cryptorefills-catalog/
    SKILL.md           # Browse and search skill
    references/        # Product types, search guide, categories
  cryptorefills-buy/
    SKILL.md           # MCP purchase workflow skill
    references/        # MCP tools, payments, order lifecycle, troubleshooting
  cryptorefills-x402/
    SKILL.md           # Autonomous x402 commerce skill
    references/        # Protocol, endpoints, troubleshooting
```

## Adding a New Skill

1. Create `skills/<skill-name>/`
2. Add `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: skill-name
   description: Short description (max 1024 chars)
   ---
   ```
3. Write agent instructions in Markdown (under 500 lines)
4. Optionally add `references/` with detailed documentation
5. Bump `version` in both `plugin.json` and `marketplace.json`

## Naming Conventions

- Skill names: lowercase, hyphens only
- Directory name **must match** the `name` field in SKILL.md frontmatter
- Prefix with `cryptorefills-` for Cryptorefills product skills

## Publishing Updates

After modifying skills, bump `version` in `.claude-plugin/plugin.json` and `marketplace.json`. Users with auto-update receive changes at next startup; others run:

```shell
/plugin marketplace update cryptorefills-skills
```

## Specification

- Plugin format: [Claude Code plugins docs](https://docs.claude.com/en/docs/claude-code/plugins)
- Marketplace format: [Plugin marketplaces docs](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)
- Skill format: [Agent Skills specification](https://agentskills.io/specification)
