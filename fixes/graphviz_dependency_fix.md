# Graphviz Dependency Fix

## Issue

The test suite was failing with the following error:

```
ImportError while importing test module '/Users/admin/code/newstart/dawn/tests/core/test_chat_planner_handlers.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/local/lib/python3.10/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests/core/test_chat_planner_handlers.py:20: in <module>
    from examples.chat_planner_workflow import (
examples/chat_planner_workflow.py:34: in <module>
    from core.utils.visualizer import visualize_workflow
core/utils/visualizer.py:4: in <module>
    import graphviz
E   ModuleNotFoundError: No module named 'graphviz'
```

The error occurs because the `visualizer.py` module has a hard dependency on the `graphviz` package, but this package might not be installed in all environments.

## Root Cause

There are two related issues:

1. The `graphviz` Python module was being imported unconditionally, causing import errors when the module wasn't available
2. The visualization functionality is not critical for the core functionality of the application, but it was blocking tests from running

## Solution

We modified the `core/utils/visualizer.py` file to make it more resilient when `graphviz` is not installed:

1. Wrapped the import with a try-except block to gracefully handle missing dependencies
2. Added a global flag `GRAPHVIZ_AVAILABLE` to track if the dependency is available
3. Modified the `visualize_workflow` function to check this flag and return early with a warning if graphviz is not available
4. Replaced `print` statements with proper logging to make it easier to debug issues

## Implementation Details

### Before:

```python
import re
from typing import Any, Dict, List, Optional

import graphviz
import networkx as nx

from core.task import Task
from core.workflow import Workflow

# ...

def visualize_workflow(...):
    # Function assumed graphviz was available
    # ...
```

### After:

```python
import re
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Try to import graphviz but make it optional
GRAPHVIZ_AVAILABLE = False
try:
    import graphviz
    import networkx as nx
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    logger.warning("Graphviz module not installed. Visualization features will be disabled.")

from core.task import Task
from core.workflow import Workflow

# ...

def visualize_workflow(...):
    if not GRAPHVIZ_AVAILABLE:
        logger.warning("Cannot visualize workflow: graphviz module not installed.")
        logger.info("To enable visualization, install graphviz with: pip install graphviz")
        logger.info("And ensure the system Graphviz package is installed (https://graphviz.org/download/)")
        return None
    
    # Rest of function is unchanged
    # ...
```

## Testing

Added new test cases to verify the fixes:

1. The test suite now runs successfully even without the graphviz module installed
2. Added specific tests for the `validate_plan_handler` function to handle nested JSON structures

## Installation Notes

To enable visualization features, users should:

1. Install the Python graphviz package: `pip install graphviz`
2. Install the system Graphviz executable from https://graphviz.org/download/ 