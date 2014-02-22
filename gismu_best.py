#!/usr/bin/env python

# Lojban gismu candidate score evaluation script
# Version 0.4

# Copyright 2014 Riley Martinez-Lynch, except where
# Copyright 2012 Arnt Richard Johansen.
# Distributed under the terms of the GPL v3.

# Usage:
#
#   python gismu_score.py uan rakan ekspekt esper predpologa mulud > scores.data
#   python gismu_best.py < scores.data
#

import platform
import sys

from marshal import load

from gismu_utils import GismuMatcher

def main(scores, gismu_file):

  print >>sys.stderr, "Sorting scores..."
  scores.sort(lambda x,y:cmp(y[0], x[0]))

  print >>sys.stderr, ""
  print >>sys.stderr, "10 first gismu candidates are:"
  print >>sys.stderr, ""
  for record in scores[:10]:
      print >>sys.stderr, record

  print >>sys.stderr, ""
  print >>sys.stderr, "Exluding candidates similar to existing gismu..."
  matcher = GismuMatcher(gismu_file)
  for (score, candidate, _) in scores:
      gismu = matcher.find_similar_gismu(candidate)
      if gismu == None:
          print >>sys.stderr, "The winner is....\n"
          print candidate.upper()
          print >>sys.stderr, ""
          break
      else:
          print >>sys.stderr, \
            "Candidate '%s' too much like gismu '%s'." % (candidate, gismu)
  else:
      print >>sys.stderr, "No suitable candidates in top 10 scores."

if __name__ == '__main__':

    gismu_path = 'gismu-list.txt'
    print >>sys.stderr, "Reading list of gismu... "
    gismu_file = file(gismu_path)

    print >>sys.stderr, "Loading scores... ",
    scores = load(sys.stdin)
    print >>sys.stderr, "%d scores loaded." % len(scores)

    main(scores, gismu_file)

