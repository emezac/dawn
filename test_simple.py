#!/usr/bin/env python3
"""Simple test to verify pytest is working."""  # noqa: D202

import unittest

class SimpleTest(unittest.TestCase):
    def test_simple(self):
        """Simple test to verify unittest is working."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main() 