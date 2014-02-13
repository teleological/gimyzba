#! /usr/bin/python

## Usage: see gismu_score.py

# Get some features
from gismu_utils import  check_for_similarity
from cPickle import load
import sys

# Load.
scores = load(sys.stdin)
print >>sys.stderr,"%d scores loaded." % len(scores)

# Sort.
print >>sys.stderr,"Sorting scores..."
scores.sort(lambda x,y:cmp(y[0],x[0]))
print >>sys.stderr,"Done."

# Eye candy.
print >>sys.stderr,"10 first gismu are:"
for item in scores[:10]:
    print >>sys.stderr,item

# Search for best match.
print >>sys.stderr,"Exluding candidates similar to already existing gismu..."
gismu_list = file('gismu-list')
for (score,gismu,_) in scores:
    if not check_for_similarity(gismu, gismu_list):
        print >>sys.stderr,"Dropping gismu %s."%gismu
    else:
        print >>sys.stderr,"The winner is....\n\n\n"
        print gismu.upper()
        break
else:
    print >>sys.stderr,"No suitable gismu (duh?)"
    

