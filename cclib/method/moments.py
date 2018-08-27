# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, the cclib development team
#
# This file is part of cclib (http://cclib.github.io) and is distributed under
# the terms of the BSD 3-Clause License.

"""Calculation of electric multipole moments based on data parsed by cclib."""

import numpy

from cclib.parser.utils import convertor
from cclib.method.calculationmethod import Method


class Moments(Method):
    def __init__(self, data):
        self.required_attrs = ('atomcoords', 'atomcharges')

        super(Moments, self).__init__(data)

    def __str__(self):
        """Returns a string representation of the object."""
        return "Multipole moments of %s" % (self.data)

    def __repr__(self):
        """Returns a representation of the object."""
        return 'Moments("%s")' % (self.data)

    def _calculate_dipole(self, charges, coords, origin):
        coords_au = convertor(coords, 'Angstrom', 'bohr')
        
        if self.data.charge == 0:
            dipole = numpy.dot(charges, coords_au)
        else:
            origin_au = convertor(origin, 'Angstrom', 'bohr')
            dipole = numpy.dot(charges, coords_au - origin_au)
            
        return convertor(dipole, 'ebohr', 'Debye')

    def _calculate_quadrupole(self, charges, coords, origin):
        transl_coords_au = convertor(coords - origin, 'Angstrom', 'bohr')

        delta = numpy.eye(3)
        Q = numpy.zeros([3,3])
        for i in range(3):
            for j in range(3):
                for q, r in zip(charges, transl_coords_au):
                    Q[i,j] += q * (3 * r[i] * r[j] - \
                              numpy.linalg.norm(r)**2 * delta[i][j])

        triu_idxs = numpy.triu_indices_from(Q)
        raveled_idxs = numpy.ravel_multi_index(triu_idxs, Q.shape)
        quadrupole = numpy.take(Q.flatten(), raveled_idxs)
        
        return convertor(quadrupole, 'ebohr2', 'Buckingham')
    
    def calculate(self, origin='nuccharge', population='mulliken',
                  masses=None, overwrite=False):
        """Calculate electric dipole and quadrupole moments using parsed
        partial atomic charges.
        
        Inputs:
            origin - a choice of the origin of coordinate system. Can
                be either a three-element iterable or a string. If
                iterable, then it explicitly defines the origin (in
                Angstrom). If string, then the value can be any one
                of the following and it describes what is used as the
                origin:
                    * 'nuccharge' -- center of positive nuclear charge
                    * 'mass' -- center of mass
            population - a type of population analysis used to extract
                corresponding atomic charges from the output file.
            masses - if None, then use default atomic masses. Otherwise,
                the user-provided will be used.
            overwrite - it defines whether to modify the data object
                or just return results. If `moments` attribute already
                exists, the old value will be fully replaced.

        Returns:
            A list where the first element is the origin of
            coordinates, while other elements are dipole and
            quadrupole moments expressed in terms of Debye and
            Buckingham units respectively.
        """
        coords = self.data.atomcoords[-1]
        try:
            charges = self.data.atomcharges[population]
        except KeyError:
            raise ValueError

        if hasattr(origin, '__iter__') and not isinstance(origin, str):
            origin_pos = numpy.asarray(origin)
        elif origin == 'nuccharge':
            origin_pos = numpy.average(coords, weights=self.data.atomnos, axis=0)
        elif origin == 'mass':
            if masses:
                atommasses = numpy.asarray(masses)
            else:
                atommasses = self.data.atommasses
            origin_pos = numpy.average(coords, weights=atommasses, axis=0)
        else:
            raise ValueError

        dipole = self._calculate_dipole(charges, coords, origin_pos)
        quadrupole = self._calculate_quadrupole(charges, coords, origin_pos)
        moments = [origin_pos, dipole, quadrupole]
        
        if overwrite:
            if hasattr(self.data, 'moments'):
                msg = ("Overwriting existing moments attribute values "
                       "with newly calculated ones.")
                self.logger.info(msg)
            self.data.moments = moments

        return moments
