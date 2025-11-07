# Claude Code Auto Bug Fixer

## Usage

### Direct

```bash
python CLAUDE_AUTO_LINTER.py once
```

### In Claude Code (with --dangerously-skip-permissions)

```python
from task_agent import Task

agent = Task(
    subagent_type="novaquote_bug_fixer",
    description="Auto Bug Fixer NOVAQUOTE Trading System",
    prompt="Execute automatic bug fixing",
    model="sonnet"
)
```

## What it does

- **Phase 1**: Python (Black, isort) + TypeScript (ESLint, Prettier)
- **Phase 2**: Python advanced (autoflake, autopep8, pyupgrade)
- **Phase 3**: Intelligent CLI auto-correction (modifies source code)

## Files

- `CLAUDE_AUTO_LINTER.py` - Main sub-agent
- `auto_bug_fixer_cli.py` - CLI auto-correction tool
- `eslint.config.js` - ESLint config
- `.prettierrc` - Prettier config
- `package.json`, `tsconfig.json` - Project configs
