# This file is part of cclib (http://cclib.github.io), a library for parsing
# and interpreting the results of computational chemistry packages.
#
# Copyright (C) 2015, the cclib development team
#
# The library is free software, distributed under the terms of
# the GNU Lesser General Public version 2.1 or later. You should have
# received a copy of the license along with cclib. You can also access
# the full license online at http://www.gnu.org/copyleft/lgpl.html.

"""Unit tests for parser utils module."""

import unittest

import cclib


class convertorTest(unittest.TestCase):

    def test_basic(self):
        """Are some basic conversions correct?"""
        convertor = cclib.parser.utils.convertor
        self.assertAlmostEqual(convertor(1.89, "bohr", "Angstrom"), 1.0, places=3)
        self.assertAlmostEqual(convertor(0.529, "Angstrom", "bohr"), 1.0, places=3)
        self.assertAlmostEqual(convertor(627.5, "kcal", "hartree"), 1.0, places=3)

    def test_pairs(self):
        """Do flipped conversions correspond to each other?"""

        convertor = cclib.parser.utils.convertor

        pairs_proportional = (
            ("Angstrom", "bohr"),
            ("cm-1", "eV"), ("cm-1", "kcal"), ("eV", "kJmol-1"),
            ("coulomb", "e"),
        )
        pairs_inverse = (("nm", "cm-1"),)

        for unit1, unit2 in pairs_proportional:
            conv1 = convertor(1.0, unit1, unit2)
            conv2 = 1.0 / convertor(1.0, unit2, unit1)
            self.assertAlmostEqual((conv1 - conv2) / conv1, 0.0)
        for unit1, unit2 in pairs_inverse:
            conv1 = convertor(1.0, unit1, unit2)
            conv2 = convertor(1.0, unit2, unit1)
            self.assertAlmostEqual((conv1 - conv2) / conv1, 0.0)


class PeriodicTableTest(unittest.TestCase):

    def setUp(self):
        self.pt = cclib.parser.utils.PeriodicTable()

    def test_elements(self):
        """Does the periodic table give correct elements?"""
        self.assertEquals(self.pt.element[6], 'C')
        self.assertEquals(self.pt.element[44], 'Ru')

    def test_elements(self):
        """Does the periodic table give correct atom numbers?"""
        self.assertEquals(self.pt.number['C'], 6)
        self.assertEquals(self.pt.number['Au'], 79)


if __name__ == "__main__":
    unittest.main()
