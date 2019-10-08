import unittest

from unittest_helpers import PEPHelper

"""
Tests PEP8 compliance of code using PEP8 helper
"""


class TestPEP8(PEPHelper, unittest.TestCase):
    def test_pep8(self):
        result = self.pep8_check()
        self.assertEqual(result.total_errors, 0, 'PEP8 validation fails. Errors count: %s' % result.total_errors)
