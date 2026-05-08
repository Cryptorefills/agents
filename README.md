# Cryptorefills Agent Skills

AI agent commerce: buy gift cards, top up phones, and get travel eSIMs with Bitcoin, ETH, SOL, USDC, USDT, Litecoin, Dogecoin, and 15+ cryptos on Solana, Ethereum, Base, Polygon, Arbitrum, Tron, and more. **No account, no CLI install, no API key** — connect via MCP or let your agent pay autonomously with x402.

| | |
|---|---|
| **Skills** | 3 (`cryptorefills-catalog`, `cryptorefills-buy`, `cryptorefills-x402`) |
| **Brands** | 10,500+ |
| **Countries** | 180+ |
| **Languages** | 10 |
| **Setup** | Zero — no account, no npm install, no API key |
| **Plugin format** | [Claude Code / Cowork](https://docs.claude.com/en/docs/claude-code/plugins) |
| **Spec** | [Agent Skills](https://agentskills.io/specification) |

## Installation

```shell
npx skills add cryptorefills/agents
```

For a specific agent:

```shell
npx skills add cryptorefills/agents -a cursor -y
```

### Claude Code

```shell
/plugin marketplace add cryptorefills/agents
/plugin install cryptorefills@cryptorefills-skills
```

### Claude Cowork

Settings > Plugins > Add marketplace `cryptorefills/agents` > Install **cryptorefills**

## Available Skills

| Skill | Description |
|-------|-------------|
| **cryptorefills-catalog** | Search and explore 10,500+ gift cards, mobile top-ups, and eSIMs across 180+ countries via MCP. Multi-language, real-time pricing, no account required. |
| **cryptorefills-buy** | Full purchase workflow via MCP — interactive guided elicitation, fixed and range-based pricing, multi-product orders, all crypto payment methods. No CLI install needed. |
| **cryptorefills-x402** | Autonomous agent commerce via [x402 protocol](https://docs.x402.org/). Two settlement rails: USDC on Base (EIP-3009) or USDC SPL on Solana mainnet (partial-signed v0 transaction). No account, no OAuth, no API key, and no native gas needed on either rail. For AI agents with a Base or Solana wallet. |

## How It Works

**cryptorefills-catalog** connects to the Cryptorefills MCP server for product discovery. No credentials needed — search by brand, country, category, or keyword in 10 languages.

**cryptorefills-buy** uses the same MCP server for the full purchase lifecycle: search → price → validate → order → pay → track delivery. Supports Bitcoin, Lightning, ETH, USDC, USDT, and more. Includes an interactive `purchaseElicitation` mode that guides the agent step-by-step through the entire purchase — the simplest path from intent to delivered gift card.

**cryptorefills-x402** enables fully autonomous purchasing using the [x402 protocol](https://docs.x402.org/) — HTTP 402 Payment Required as a machine-to-machine payment standard. Agents pick a settlement rail per request: **Base** (USDC, signed via EIP-712 / EIP-3009 `transferWithAuthorization`; Cryptorefills relays on-chain so no ETH is needed) or **Solana** (USDC SPL on mainnet, partial-signed v0 transaction with the CDP facilitator as fee-payer so no SOL is needed). Either way, no account or API key.

## Country Code Formats

> **Important**: The MCP skills (`cryptorefills-catalog`, `cryptorefills-buy`) use **uppercase** country codes (`US`, `IT`, `BR`). The x402 skill (`cryptorefills-x402`) uses **lowercase** country codes (`us`, `it`, `br`). Always use the correct case for the endpoint you're calling.

## MCP Server

```
URL: https://api.cryptorefills.com/mcp/http
Header: User-Agent: Cryptorefills-MCP/1.0
```

## x402 Endpoints

Two hosts, same REST contract. Pick by rail:

```
Multi-rail (Base default; opt into Solana with X-Preferred-Network: solana)
  URL:      https://x402.cryptorefills.com
  Manifest: https://x402.cryptorefills.com/.well-known/x402.json

Solana-only (host-pinned; for registries like pay-skills that demand a Solana 402 by default)
  URL:      https://solana.x402.cryptorefills.com
  Manifest: https://solana.x402.cryptorefills.com/.well-known/x402.json

Base rail:    USDC on Base (chain 8453, contract 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913)
Solana rail:  USDC SPL on mainnet (mint EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v)
```

## Contributing

1. Fork the repository
2. Create a skill in `skills/<skill-name>/`
3. Add `SKILL.md` with YAML frontmatter + Markdown instructions
4. Optionally add `references/` for detailed docs
5. Bump version in `.claude-plugin/plugin.json` and `marketplace.json`
6. Submit a pull request

## License

[MIT](LICENSE)
