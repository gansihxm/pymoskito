#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_modules
----------------------------------

Tests for simulation modules.
"""

import unittest
from collections import OrderedDict
import pickle
import os

import scipy.signal as sig
import numpy as np

import pymoskito as pm
from pymoskito.simulation_modules import (
    SimulationModule, Model
)


class DummyModule(SimulationModule):
    """
    Possibly the dumbest implementation of a Simulation Module

    The attribute 'public_settings' is implemented as ordered dict to have
    control over the order in which the entries will appear in the settings
    window.
    """
    public_settings = OrderedDict()

    def calc_output(self, input_vector):
        """
        This method has to be implemented, returning the input should do the
        job.
        """
        return "bazz"


class TestSimulationModule(unittest.TestCase):
    def setUp(self):
        pass

    def test_init(self):
        # Type Error due to abstract base class
        with self.assertRaises(TypeError):
            SimulationModule()

        # Initialization has te be done with correct settings
        with self.assertRaises(AssertionError):
            DummyModule(settings=None)

        # This is the easiest way
        settings = DummyModule.public_settings

        # check default attributes
        m = DummyModule(settings)
        m._settings["tick divider"] = 1
        m._settings["step width"] = None

        # modules entry has to be deleted after init is completed
        with self.assertRaises(KeyError):
            m._settings["modules"]

        # check acquisition of attributes
        settings["tick divider"] = 1234
        settings["step width"] = 13.26  # this _CANNOT_ be known a priori
        m = DummyModule(settings)
        self.assertEqual(m._settings["tick divider"], 1234)
        self.assertEqual(m._settings["step width"], None)

    def test_properties(self):
        settings = DummyModule.public_settings
        settings["tick divider"] = 1234
        settings["step width"] = 13.26  # this _CANNOT_ be known a priori
        m = DummyModule(settings)

        self.assertTrue(isinstance(m.public_settings, OrderedDict))

        self.assertEqual(m.tick_divider, 1234)
        self.assertEqual(m.step_width, None)

        m.step_width = 13.37
        self.assertEqual(m.step_width, 13.37)

    def test_calc_output(self):
        settings = DummyModule.public_settings
        settings["tick divider"] = 1234
        settings["step width"] = 13.26  # this _CANNOT_ be known a priori
        m = DummyModule(settings)

        input_data = dict(foo="bar")  # later dict of pairs module-type: output
        out = m.calc_output(input_data)


class DummyModel(Model):

    public_settings = OrderedDict([("initial state", [1, 2, 3, 4])])

    def __init__(self, settings):
        super().__init__(settings)

    def state_function(self, t, x, args):
        return np.zeros((4,))

    def calc_output(self, input_vector):
        return 0


class TestModel(unittest.TestCase):

    def test_init(self):
        settings = OrderedDict([("initial state", [1, 2, 3, 4])])

        # input_count and state_count are missing
        with self.assertRaises(AssertionError):
            DummyModel(settings)

        settings["input_count"] = 1
        settings["state_count"] = 3

        # state count oes not match initial state
        with self.assertRaises(AssertionError):
            DummyModel(settings)

        settings["state_count"] = 4
        m = DummyModel(settings)

    def test_properties(self):
        settings = OrderedDict([("initial state", [1, 2, 3, 4])])
        settings["input_count"] = 1
        settings["state_count"] = 4
        m = DummyModel(settings)

        self.assertEqual(m.initial_state, [1, 2, 3, 4])


class StateSpaceModelTest(unittest.TestCase):

    def setUp(self):
        # generate StateSpace model
        self.sys = sig.TransferFunction([5], [10, 1]).to_ss()

        if not os.path.exists("test_sys.dat"):
            with open("test_sys.dat", "wb") as f:
                pickle.dump(self.sys, f)

    def test_init(self):
        settings = pm.LinearStateSpaceModel.public_settings

        # path should point to a real file
        settings["config file"] = "A: [2, 3], B = 1"
        with self.assertRaises(AssertionError):
            pm.LinearStateSpaceModel(settings)

        # neither initial state nor initial output present
        settings["config file"] = "test_sys.dat"
        with self.assertRaises(ValueError):
            pm.LinearStateSpaceModel(settings)

        x0 = np.array([12])
        settings["initial state"] = x0
        m = pm.LinearStateSpaceModel(settings)
        self.assertEqual(m.initial_state, x0)

        settings["initial ouput"] = self.sys.C @ x0
        m = pm.LinearStateSpaceModel(settings)
        self.assertEqual(m.initial_state, x0)


if __name__ == '__main__':
    unittest.main()