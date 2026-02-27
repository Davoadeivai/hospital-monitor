"""
Core app configs and monkeypatches
"""
import sys

# ==============================================================================
# Monkeypatch for Django 4.2 + Python 3.14 Compatibility Issue
# Error: AttributeError: 'super' object has no attribute 'dicts' in Context.__copy__
# ==============================================================================
if sys.version_info >= (3, 14):
    from django.template import context
    
    def _patched_context_copy(self):
        duplicate = super(context.BaseContext, self).__copy__()
        duplicate.dicts = self.dicts[:]
        return duplicate

    context.BaseContext.__copy__ = _patched_context_copy
