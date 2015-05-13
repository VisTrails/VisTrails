"""Scripting integration in VisTrails.

This package contains logic to convert VisTrails pipelines to/from Python
scripts.
"""

from __future__ import division

from vistrails.core.scripting.export import write_workflow_to_python
from vistrails.core.scripting.scripts import Prelude, Script


__all__ = ['Prelude', 'Script', 'write_workflow_to_python']
