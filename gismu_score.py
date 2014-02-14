#!/usr/bin/env python

# Lojban gismu candidate creation and evaluation script
# Version 0.2

# Copyright 2014 Riley Martinez-Lynch, except where
# Copyright 2012 Arnt Richard Johansen.
# Distributed under the terms of the GPL v3.

# Usage:
#
#   python gismu_score.py uan rakan ekspekt esper predpologa mulud > scores.data
#   python gismu_best.py < scores.data
#

import sys
import threading
import Queue
import anydbm

from cPickle import dump

from gismu_utils import GismuGenerator, GismuScorer

class QueueWorker(threading.Thread):

    def __init__(self, input_queue, output_queue, scorer):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.scorer = scorer
        threading.Thread.__init__(self)

    def run(self):
        processed = 0
        while 1:
            candidate = self.read_input()
            if candidate == None:
                break
            self.process_input(candidate)

            processed += 1
            print >>sys.stderr, "\010" * 9, # backspace
            print >>sys.stderr, processed,

    def read_input(self):
        candidate = None
        try:
            candidate = self.input_queue.get(True, 2) # block for up to 2s
        except Queue.Empty:
            pass
        return candidate

    def process_input(self, candidate):
        weighted_score, language_scores = self.scorer.compute_score(candidate)
        self.output_queue.put((weighted_score, candidate, language_scores))

##

def read_or_generate_persisted_candidates(db_path, generator):
    try:
        db = anydbm.open(db_path)
        print >>sys.stderr, "Consulting precompiled database..."
    except:
        print >>sys.stderr, "Generating new database..."
        db = anydbm.open(db_path, 'c')
        generate_and_persist_candidates(generator, db)
        db.close()
        db = anydbm.open(db_path)
    return db.keys()

def generate_and_persist_candidates(generator, db):
    print >>sys.stderr, "Generating candidates..."
    candidates = generator.generate()
    print >>sys.stderr, "Filtering and storing candidates..."
    for i, candidate in enumerate(candidates, 1):
        if i % 100 == 0:
            print >>sys.stderr, '\r     \r%d' % i,
        db[candidate] = ""
    print >>sys.stderr, "\rDone       "

def compute_scores(candidates, scorer, number_of_workers):
    input_queue = Queue.Queue()
    for candidate in candidates:
        input_queue.put(candidate)
    output_queue = Queue.Queue()

    workers = []
    for x in xrange(number_of_workers):
        worker = QueueWorker(input_queue, output_queue, scorer)
        worker.start()
        workers.append(worker)
    for worker in workers:
        worker.join()
    return read_scores(output_queue)

def read_scores(score_queue):
    scores = []
    queue_empty = False
    while not queue_empty:
        try:
            score = score_queue.get_nowait()
            scores.append(score)
        except Queue.Empty:
            queue_empty = True
    return scores

if __name__ == '__main__':

    db_path = 'candidates.db'

    worker_count = 1 # performance on cpython degrades with > 1 worker

    words = sys.argv[1:7]
    for word in words:
        if len(word) < 2:
            raise ValueError("Input words must be at least two letters long")

    generator = GismuGenerator()
    candidates = \
        read_or_generate_persisted_candidates(db_path, generator)
    print >>sys.stderr, "%d candidates read." % len(candidates)

    print >>sys.stderr, "Scoring candidates..."
    scorer = GismuScorer(words)
    scores = compute_scores(candidates, scorer, worker_count)

    print >>sys.stderr, "\rDumping scores to STDOUT.      "
    dump(scores, sys.stdout, 2)

