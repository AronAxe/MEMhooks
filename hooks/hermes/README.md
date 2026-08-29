# Hermes pre-LLM hook

Hermes has a real `pre_llm_call` lifecycle hook. MemHooks uses it so loading `MEMHOOKS.md` does **not** depend on the model remembering to open the file itself.

The included [`memhooks_pre_llm.py`](memhooks_pre_llm.py) script:

1. receives Hermes' shell-hook JSON payload on stdin;
2. reads the actual working directory from `cwd`;
3. finds the workspace root (`MEMHOOKS_ROOT`, nearest Git root, or highest ancestor containing `MEMHOOKS.md`);
4. walks root → current directory;
5. reads every applicable `MEMHOOKS.md`;
6. honors `inherits: false` deterministically;
7. returns `{"context": "..."}` to Hermes;
8. Hermes injects that context into the current user message **before the tool/LLM loop starts**.

No LLM is called by the loader itself.

## Install

```bash
mkdir -p ~/.hermes/agent-hooks
cp hooks/hermes/memhooks_pre_llm.py ~/.hermes/agent-hooks/
chmod +x ~/.hermes/agent-hooks/memhooks_pre_llm.py
```

Then add this to `~/.hermes/config.yaml`:

```yaml
hooks:
  pre_llm_call:
    - command: "python3 ~/.hermes/agent-hooks/memhooks_pre_llm.py"
      timeout: 5
```

Hermes asks for consent the first time it sees a new shell hook. For a non-interactive Gateway/Desktop startup, use Hermes' normal hook-approval mechanism after reviewing the script (for example `hooks_auto_accept: true` if that is appropriate for your setup).

## What is guaranteed

With the hook installed, the applicable `MEMHOOKS.md` files are loaded **before every user-turn LLM call**. The model does not need to decide to search the filesystem for them.

The hook deliberately does **not** directly query Hindsight/OpenViking/Honcho itself. Doing that would hard-wire MemHooks to a memory API. Instead it injects the concrete retrieval routing before the model call; the agent then executes those specific searches through whichever memory tools are actually available during the same turn.

That preserves the core design:

> **MemHooks specifies what must be recalled here. The installed memory system decides how.**

## Bounds

Defaults:

- `MEMHOOKS_MAX_CHARS=24000` total injected characters
- `MEMHOOKS_MAX_FILE_CHARS=12000` per file
- `MEMHOOKS_FILENAME=MEMHOOKS.md`
- `MEMHOOKS_ROOT=/explicit/workspace/root` can override root detection

All can be set as environment variables.

If no applicable hook exists, the script returns `{}` and Hermes continues normally.

## Test manually

From inside a project with a `MEMHOOKS.md`:

```bash
printf '%s' '{"hook_event_name":"pre_llm_call","cwd":"'"$(pwd)"'","extra":{}}' \
  | python3 ~/.hermes/agent-hooks/memhooks_pre_llm.py
```

You should receive JSON containing a `context` field with the applicable hook chain.

Hermes' own hook utilities can then be used to inspect/test the registered hook.
