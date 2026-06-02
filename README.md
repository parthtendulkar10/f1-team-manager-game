# f1-team-manager-game

Interactive text-based F1 team owner/manager simulation with dynamic AI-generated personalities, events, negotiations, and race narratives.

## Features

- Manufacturer + Team Principal selection with distinct backgrounds/stat profiles
- AI-generated personalities for principal, drivers, and staff
- Dynamic events (driver disputes, engineering conflicts, sponsor/media pressure)
- Multi-season progression with budget, development, morale, chemistry, and owner confidence
- Driver market unlocks stronger candidates as results improve
- Save/load game state with AI context persistence
- OpenAI or Anthropic integration via environment variables, with offline fallback generation

## Quick Start

```bash
python main.py
```

## Optional AI Configuration

Use one provider:

```bash
export OPENAI_API_KEY="your-key"
# optional
export OPENAI_MODEL="gpt-4.1-mini"
```

or

```bash
export ANTHROPIC_API_KEY="your-key"
# optional
export ANTHROPIC_MODEL="claude-3-5-haiku-latest"
```

Without these keys, the game uses deterministic procedural fallback generation.

## Tests

```bash
python -m unittest discover -s tests -v
```
