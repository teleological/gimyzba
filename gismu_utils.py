
# Lojban gismu candidate generation and scoring utilities
# Version 0.2

# Copyright 2014 Riley Martinez-Lynch, except where
# Copyright 2012 Arnt Richard Johansen.
# Distributed under the terms of the GPL v3.

import sys
import re
import mlpy

from itertools import chain, ifilter

C = 'bcdfgjklmnprstvxz'
V = 'aeiou'

CCVCV = [ C, C, V, C, V ]
CVCCV = [ C, V, C, C, V ]

VALID_CC_INITIALS = [ 'bl', 'br',
                      'cf', 'ck', 'cl', 'cm', 'cn', 'cp', 'cr', 'ct',
                      'dj', 'dr', 'dz',
                      'fl', 'fr',
                      'gl', 'gr',
                      'jb', 'jd', 'jg', 'jm', 'jv',
                      'kl', 'kr',
                      'ml', 'mr',
                      'pl', 'pr',
                      'sf', 'sk', 'sl', 'sm', 'sn', 'sp', 'sr', 'st',
                      'tc', 'tr', 'ts',
                      'vl', 'vr',
                      'xl', 'xr',
                      'zb', 'zd', 'zg',
                      'zm', 'zv' ]

FORBIDDEN_CC = [ 'cx', 'kx', 'xc', 'xk', 'mz' ]

SIBILANT = 'cjsz'
VOICED   = 'bdgvz'
UNVOICED = 'cfkpstx'

SIMILARITIES = { 'b':'pv',
                 'c':'js',
                 'd':'t',
                 'f':'pv',
                 'g':'kx',
                 'j':'cz',
                 'k':'gx',
                 'l':'r',
                 'm':'n',
                 'n':'m',
                 'p':'bf',
                 'r':'l',
                 's':'cz',
                 't':'d',
                 'v':'bf',
                 'x':'gk',
                 'z':'js' }

# Per CLL 4.14: http://dag.github.io/cll/4/14
LANGUAGE_WEIGHTS = (0.347, 0.196, 0.160, 0.123, 0.089, 0.085)

XADD = lambda a,b: [x+y for x in a for y in b]

class GismuGenerator:

    def __init__(self, cc_shape = CCVCV, cv_shape = CVCCV):
      self.cc_shape = cc_shape
      self.cv_shape = cv_shape

    def generate(self):
        return chain(ifilter(self.check_cc_initials, reduce(XADD, self.cc_shape)),
                     ifilter(self.check_cv_internals, reduce(XADD, self.cv_shape)))

    def check_cc_initials(self, candidate):
        return candidate[:2] in VALID_CC_INITIALS

    def check_cv_internals(self, candidate):
        return candidate[2] != candidate[3] and \
          not (candidate[2] in VOICED   and candidate[3] in UNVOICED) and \
          not (candidate[2] in UNVOICED and candidate[3] in VOICED  ) and \
          not (candidate[2] in SIBILANT and candidate[3] in SIBILANT) and \
          candidate[2:4] not in FORBIDDEN_CC

class GismuScorer:

    def __init__(self, language_words, weights = LANGUAGE_WEIGHTS):
        self.words_chrs = [ [ ord(y) for y in list(x) ] for x in language_words ]
        self.weights = weights

    def compute_score(self, candidate):
        candidate_chrs = [ ord(x) for x in list(candidate) ]
        language_scores = self.compute_language_scores(candidate_chrs)
        weighted_score = self.calculate_weighted_score(language_scores)
        return weighted_score, language_scores

    def compute_language_scores(self, candidate_chrs):
      return [ self.compute_language_score(candidate_chrs, lang_chrs) \
                 for lang_chrs in self.words_chrs ]

    def compute_language_score(self, candidate_chrs, lang_chrs):
        length, path = mlpy.lcs_std(candidate_chrs, lang_chrs)
        if length < 2:
            score = 0
        elif length == 2:
            score = self.qualified_dyad_score(path, candidate_chrs, lang_chrs)
        else:
            score = length
        return score

    def qualified_dyad_score(self, path, candidate_chrs, lang_chrs):
        candidate_chrs_distance = path[0][1] - path[0][0]
        path_chrs_distance = path[1][1] - path[1][0]
        if candidate_chrs_distance == 1 and path_chrs_distance == 1:
            score = 2
        elif candidate_chrs_distance == 2 and path_chrs_distance == 2:
            score = 2
        else:
            score = self.score_dyad_by_regex(candidate_chrs, lang_chrs)
        return score

    def score_dyad_by_regex(self, candidate_chrs, lang_chrs):
        patterns = self.gismu_dyad_patterns(candidate_chrs)
        lang_word = self.chrs_to_string(lang_chrs)
        return self.score_for_regex(patterns, lang_word, 2)

    def gismu_dyad_patterns(self, candidate_chrs):
        g, i, s, m, u = [ chr(x) for x in candidate_chrs ]
        return [ '%s(%s|.%s)' % (g,i,s),
                 '%s(%s|.%s)' % (i,s,m),
                 '%s(%s|.%s)' % (s,m,u),
                 '%s%s' % (m,u) ]

    def chrs_to_string(self, chrs):
        return ''.join([ chr(x) for x in chrs ])

    def score_for_regex(self, patterns, word, value):
        score = 0
        for pattern in patterns:
            if re.search(pattern, word):
                score = value
                break
        return score

    def calculate_weighted_score(self, scores):
        # Multiply each score by the given weight, then sum weighted scores
        return reduce(float.__add__,
                      map(float.__mul__, map(float, scores), self.weights))

class GismuDeduper:

    def __init__(self, gismu_list, stem_length = 4):
        self.gismu_list = gismu_list
        self.stem_length = stem_length

    def has_conflict(self, candidate):
        candidate = candidate.rstrip()
        similarity_pattern = map(lambda x:SIMILARITIES.get(x, '.'), candidate)
        # e.g. "rekpa" =~ /l.[gx][bf]./ where . matches NOTHING

        err = False
        gismu = None
        self.gismu_list.seek(0)
        for gismu in self.gismu_list:
            gismu = gismu.rstrip()
            err = self.compare_with_gismu(candidate, similarity_pattern, gismu)
            if err:
                break

        if err:
            print >>sys.stderr, '%s conflicts with gismu %s'% (candidate, gismu)

        return err

    def compare_with_gismu(self, candidate, gismu, similarity_pattern):
        return self.compare_gismu_stem(candidate, gismu) or \
          self.compare_gismu_structure(candidate, gismu, similarity_pattern)

    def compare_gismu_stem(self, candidate, gismu):
        return candidate[:self.stem_length] == gismu[:self.stem_length]

    # Apply similarity pattern to each position in gismu if others letters equal
    #
    # /PAT/ekpa
    # r/PAT/kpa
    # re/PAT/pa
    # rek/PAT/a
    # rekp/PAT/
    #
    def compare_gismu_structure(self, candidate, gismu, similarity_pattern):
        similar = False
        common_len = min(len(candidate), len(gismu))
        for i in xrange(common_len):
            if self.strings_match_except(candidate, gismu, i, common_len) and \
              self.test_pattern(gismu[i], similarity_pattern[i]):
                similar = True
                break
        return similar

    def strings_match_except(self, x, y, i, j):
      return x[:i] == y[:i] and x[i+1:j] == y[i+1:j]

    def test_pattern(self, letter, pattern):
        if pattern == '.':
            return False
        return letter in pattern

