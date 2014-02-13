#! /usr/bin/python

## Usage:
# python gismu_score.py uan rakan ekspekt esper predpologa mulud >scores.data
# python gismu_best.py <scores.data
## Dependencies:
# - CPU time :)
# - list of 5-letters gismu in file 'gismu-list' (one per line)

# Native language data: need 6 words
import sys
import threading
import Queue
words=sys.argv[1:7]
weights=(0.347, 0.196, 0.160, 0.123, 0.089, 0.085)

# Get some features
from gismu_utils import gen_candidates,gen_regex,compute_scores,\
     check_for_similarity
import anydbm
from cPickle import loads,dumps,dump

class ScoreThread(threading.Thread):
    def __init__(self, gismuQueue, scoreQueue, db):
        self.gismuQueue = gismuQueue
        self.scoreQueue = scoreQueue
        self.db = db
        threading.Thread.__init__(self)
    def run(self):
        # If there are any more gismu, process it
        while 1:
            try:
                gismu = self.gismuQueue.get(True, 2)
            except Queue.Empty:
                print >>sys.stderr, "\nThread exiting."
                break
            tests = loads(self.db[gismu])
            # Compute the scores and the weighted sum
            print >>sys.stderr, gismu,
            floats = map(float,compute_scores(tests,words))
            total = reduce(float.__add__,map(float.__mul__,floats,weights))
            self.scoreQueue.put((total,gismu,floats))
            print >>sys.stderr, "\010" * 7,
            

def compute_all_scores():
    # Load the gismu candidate database, or build it if it does
    # not yet exist. The database contains, for each candidate
    # gismu, a list of weighted fnmatch-style patterns.
    try:
        db=anydbm.open('candidates-regex')
        l=len(db.keys())
    except:
        db=anydbm.open('candidates-regex','c')
        print >>sys.stderr,"First run only: generating candidates..."
        candidates = gen_candidates()
        print >>sys.stderr,"First run only: generating candidate patterns..."
        l=len(candidates)
        for i,gismu in enumerate(candidates):
            if i%100==0:
                print >>sys.stderr,'\r     \r%d%%'%int((100.*float(i)/l)),
            db[gismu] = dumps(gen_regex(gismu),2)
        print >>sys.stderr,"\rDone       "
        db.close()
        db=anydbm.open('candidates-regex')

    # Get candidate gismu list from database
    candidates = db.keys()
    print >>sys.stderr,"%d candidates loaded."%len(candidates)

    # Compute the scores
    print >>sys.stderr,"Computing scores..."
    WorkQueue = Queue.Queue()
    ScoreQueue = Queue.Queue()
    for gismu in db.keys():
        WorkQueue.put(gismu)
    for x in xrange(4):
        CurrentThread = ScoreThread(WorkQueue, ScoreQueue, db)
        CurrentThread.start()
    CurrentThread.join()
    scores=[]
    QueueEmpty = False
    while not QueueEmpty:
        try:
            scoreset = ScoreQueue.get_nowait()
            scores.append(scoreset)
        except Queue.Empty:
            QueueEmpty = True
            print >>sys.stderr, "\nEmpty queue!"
    
#     for i,gismu in enumerate(db.keys()):

#         # Progress meter
#         if not i%100:
#             print >>sys.stderr,'\r       \r%4.2f%%'%(100.*float(i)/l),

#         # Load the fnmatch patterns
#         tests = loads(db[gismu])
#         # Compute the scores and the weighted sum
#         floats = map(float,compute_scores(tests,words))
#         total = reduce(float.__add__,map(float.__mul__,floats,weights))

#         scores.append((total,gismu,floats))


    print >>sys.stderr, "\rDone.      "
    print dump(scores,sys.stdout,2)

if __name__ == '__main__':
    compute_all_scores()
