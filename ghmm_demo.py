#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Tue 10 Mar 2015 12:03:14 AM CST
# File Name: try_ghmm.py
# Description:
#########################################################################

from ghmm import *

sigma = IntegerRange(1, 7)
A = [[0.9, 0.1], [0.3, 0.7]]
efair = [1.0 / 6] * 6
eloaded = [3.0 / 13, 3.0 / 13, 2.0 / 13, 2.0 / 13, 2.0 / 13, 1.0 / 13]
B = [efair, eloaded]
pi = [0.5] * 2
m = HMMFromMatrices(sigma, DiscreteDistribution(sigma), A, B, pi)
#print m

obs_seq = m.sampleSingle(20)
print obs_seq
obs = map(sigma.external, obs_seq)
print obs


