#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Sun 29 Mar 2015 10:24:11 AM CST
# File Name: edict_hmm.py
# Description:
#########################################################################

import sys
import os
sys.path.append(os.path.abspath("/home/magodo/code/python/speech/VQ"))
sys.path.append(os.path.abspath("/home/magodo/code/python/Edict/working/edict/lib/speech"))

import mfcc
import waveio
import lbg
import ghmm
import pickle
from redirector import stderr_redirector

# Model target
targets = ["apple", "beef", "egg", "lemon", "mushroom", "noodle", "orange", "spaghetti", "spam", "strawberry", "watermelon" ]
target = targets[4]
# Number of state variable(N) and observation symbols(M)
N = 6
M = 256
# Left-right model step set
tup = 2

#~~~~~~~~~~~~~~~~~~~~~~
# Load VQ
#~~~~~~~~~~~~~~~~~~~~~~
print "Begin load VQ..."
with open("/home/magodo/code/python/speech/VQ/VQ.pkl"+"-%s"%M, "r") as f:
    mu, clusters = pickle.load(f)
print "Finish load VQ."

#~~~~~~~~~~~~~~~~~~~~~~
# Create initial model
#~~~~~~~~~~~~~~~~~~~~~~
print "Begin initialize model..."
##########################
# A is left-right model
##########################
A = []
for i in range(N-tup+1):
    A.append([0] * i + [1.0 / tup] * tup + [0] * (N - tup - i))
for i in range(N-tup+1, N):
    A.append([0] * i + [1.0 / (N-i)] * (N-i))

##########################
# B is initialized based on the training set.
##########################
sample_sum = sum([len(clusters[i]) for i in clusters.keys()])
# tmp_stat is not of M possibilities
tmp_stat = [0.0000001] * M
for i in clusters.keys():
    tmp_stat[i] = len(clusters[i])/(1.0*sample_sum)
B = [tmp_stat] * N

pi = [1.0 / N] * N
codebook = ghmm.IntegerRange(0, M)
model = ghmm.HMMFromMatrices(codebook, ghmm.DiscreteDistribution(codebook), A, B, pi)
print "Finish initialize model."

#~~~~~~~~~~~~~~~~~~~~~~
# Train model
#~~~~~~~~~~~~~~~~~~~~~~
# Load two samples for strawberry and calculate their MFCC
# Create sample_seqs(List of lists of VQed MFCC)
samples = []
def feature_fetch(target, dirname, fnames):
    for fname in fnames:
        if target in fname:
            with open(os.path.join(dirname, fname)) as f:
                signal, FS = waveio.wave_from_file(f)
                samples.append(mfcc.mfcc(signal, FS))
os.path.walk("/home/magodo/code/voiceMaterial/word", feature_fetch, target)

sample_seqs = []
for sample in samples:
    sample_seq = []
    for point in sample:
        sample_seq.append(lbg.cluster_point(point, mu))
    sample_seqs.append(sample_seq)

sample_seqset = ghmm.SequenceSet(codebook, sample_seqs)

print "Begin train model..."
model.baumWelch(sample_seqset, 1, 0.0001)
print "Finish train model."

#~~~~~~~~~~~~~~~~~~~~~~
# Test model
#~~~~~~~~~~~~~~~~~~~~~~

print "Begin test model..."
# Get all samples
# Stored in feature_collection: e.g. feature_collection['egg1.wav'] = [41, 20, 22, 1, 129 ....]
print "    Begin get samples..."
feature_collection = {}
def collect_mfcc(arg, dirname, fnames):
    for fname in fnames:
        if fname.endswith(".wav"):
            signal, FS = waveio.wave_from_file(os.path.join(dirname, fname))
            feature = list(mfcc.mfcc(signal, FS))
            feature_collection[fname] = []
            for point in feature:
                feature_collection[fname].append(lbg.cluster_point(point, mu))

os.path.walk(top = "/home/magodo/code/voiceMaterial/word", func = collect_mfcc, arg = None)
print "    Finish get samples..."


# Iterate and calculate each sample's log likelihood
f = open("/dev/null", 'w')
with stderr_redirector(f):
    test_result = {}
    for sample in feature_collection.keys():
        test_result[sample] = model.loglikelihood(ghmm.EmissionSequence(codebook, feature_collection[sample]))

# Iterate and print each sample's log likelihood
test_result = sorted(test_result.items(), key = lambda item: item[1])
for sample in test_result:
    print "~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "File:              %s" %sample[0]
    print "log loglikelihood: %f"%sample[1]

print "Finish test model..."
