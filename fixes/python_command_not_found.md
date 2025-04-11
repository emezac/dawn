# Python Command Not Found Issue

## Problem

Shell scripts in the project were using the `python` command, which doesn't exist in some environments. This caused errors like:

```
./run_tests.sh: line 33: python: command not found
```

This occurs when:
1. Python is installed as `python3` instead of `python` (common on macOS and some Linux distributions)
2. The `python` command isn't in the PATH when scripts are executed 
3. When running in environments like Git hooks where PATH might be limited

## Solution

Replace direct `python` references with `/usr/bin/env python3` in all shell scripts, which is more portable and cross-platform compatible.

### Fixed files:
1. `.git/hooks/pre-commit` - For running the D202 fixer script during pre-commit
2. `run_tests.sh` - For running pytest and unittest

### Example fix:

```diff
- python -m pytest -v | tee "$TEST_OUTPUT_FILE"
+ /usr/bin/env python3 -m pytest -v | tee "$TEST_OUTPUT_FILE"
```

## Why this works

Using `/usr/bin/env python3`:
1. Uses the `env` program to find the Python interpreter in the user's PATH
2. Specifically looks for `python3`, which is more consistent across platforms
3. Works even when the shell environment is limited (like in Git hooks)

## Related issues

This fix also addresses situations where pytest and other dependencies aren't properly found. The updated test script uses unittest directly when needed as a fallback. 