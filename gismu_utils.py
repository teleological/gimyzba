# This is a Python module for use
# by scripts gismu_score.py and gismu_best.py.

# Lojban facts.
C='bcdfgjklmnprstvxz'
V='aeiou'
initCC=['bl','br',
        'cf','ck','cl','cm','cn','cp','cr','ct',
        'dj','dr','dz',
        'fl','fr',
        'gl','gr',
        'jb','jd','jg','jm','jv',
        'kl','kr',
        'ml','mr',
        'pl','pr',
        'sf','sk','sl','sm','sn','sp','sr','st',
        'tc','tr','ts',
        'vl','vr',
        'xl','xr',
        'zb','zd','zg',
        'zm','zv']
forbiddenCC=['cx','kx','xc','xk','mz']
sibilant='cjsz'
voiced='bdgvz'
unvoiced='cfkpstx'

# Utility functions.
add = lambda a,b: a+b
xadd = lambda a,b: [x+y for x in a for y in b]

# Get some features.
import re
from fnmatch import fnmatch
import sys

def gen_candidates():
    # Generate the list of all possible gismu.
    candidates=[]
    for w in reduce(xadd,[C,C,V,C,V]):
        if w[:2] not in initCC:
            continue
        candidates.append(w)
    for w in reduce(xadd,[C,V,C,C,V]):
        if w[2]==w[3] or \
               (w[2] in voiced and w[3] in unvoiced) or \
               (w[2] in unvoiced and w[3] in voiced) or \
               (w[2] in sibilant and w[3] in sibilant) or \
               w[2:4] in forbiddenCC:
            continue
        candidates.append(w)
    return candidates

def gen_patterns(gismu):
    # Generate a list of weighted fnmatch patterns
    # able to compute the score of a candidate gismu
    # w.r.t. a native language word.
    g,i,s,m,u = gismu
    return [[x[0], '*%s*'%x[1]] for x in \
                [[len(x), '*'.join(list(x))] for x in [ \
        gismu,
        g+i+s+m,
        g+i+s+u,
        g+i+m+u,
        g+s+m+u,
        i+s+m+u,
        g+i+s,
        g+i+m,
        g+i+u,
        g+s+u,
        g+s+m,
        g+m+u,
        i+s+m,
        i+m+u,
        s+m+u
        ]]+[
        (2,g+i), (2,g+'?'+s),
        (2,i+s), (2,i+'?'+m),
        (2,s+m), (2,s+'?'+u),
        (2,m+u)
        ]]

# def gen_regex(gismu):
#     import re
#     g, i, s, m, u = gismu
#     regexes = [[x[0], '*%s*'%x[1]] for x in \
#                 [[len(x), '*'.join(list(x))] for x in [ \
#         gismu,
#         g+i+s+m,
#         g+i+s+u,
#         g+i+m+u,
#         g+s+m+u,
#         i+s+m+u,
#         g+i+s,
#         g+i+m,
#         g+i+u,
#         g+s+u,
#         g+s+m,
#         g+m+u,
#         i+s+m,
#         i+m+u,
#         s+m+u
#         ]]+[
#         (2,g+i), (2,g+'?'+s),
#         (2,i+s), (2,i+'?'+m),
#         (2,s+m), (2,s+'?'+u),
#         (2,m+u)
#         ]]

# def gen_regex(gismu):
#     import re
#     g, i, s, m, u = gismu
#     regexes = [[x[0], '*%s*'%x[1]] for x in \
#                 [[len(x), '*'.join(list(x))] for x in [ \
#         gismu,
#         g+i+s+m,
#         g+i+s+u,
#         g+i+m+u,
#         g+s+m+u,
#         i+s+m+u,
#         g+i+s,
#         g+i+m,
#         g+i+u,
#         g+s+u,
#         g+s+m,
#         g+m+u,
#         i+s+m,
#         i+m+u,
#         s+m+u
#         ]]+[
#         (2,g+i), (2,g+'.'+s),
#         (2,i+s), (2,i+'.'+m),
#         (2,s+m), (2,s+'.'+u),
#         (2,m+u)
#         ]]
#    return regexes

def gen_regex(gismu):
    import re
    g, i, s, m, u = gismu
    regexes = [[x[0], '.*%s.*'%x[1]] for x in \
                [[len(x), '.*'.join(list(x))] for x in [ \
        gismu,
        g+i+s+m,
        g+i+s+u,
        g+i+m+u,
        g+s+m+u,
        i+s+m+u,
        g+i+s,
        g+i+m,
        g+i+u,
        g+s+u,
        g+s+m,
        g+m+u,
        i+s+m,
        i+m+u,
        s+m+u
        ]]+[
        (2,g+i), (2,g+'.'+s),
        (2,i+s), (2,i+'.'+m),
        (2,s+m), (2,s+'.'+u),
        (2,m+u)
        ]]
    return regexes

# def compute_scores(tests, words):
#     # Compute the scores of a list of native
#     # language words w.r.t a set of weighted
#     # fnmatch patterns (generated y gen_patterns).
#     ret=[]
#     for w in words:
#         for score,pat in tests:
#             if fnmatch(w, pat):
#                 break
#         else:
#             score=0
#         ret.append(score)
#     return ret

def compute_scores(tests, words):
    # Compute the scores of a list of native
    # language words w.r.t a set of weighted
    # regular expressions.
    ret=[]
    for word in words:
        ret.append(compute_score(tests, word))
#         for score,pat in tests:
#             if re.match(pat, w):
#                 break
#         else:
#             score=0
#         ret.append(score)
    return ret

def compute_score(tests, word):
    for score,pat in tests:
        if re.match(pat, word):
            break
        else:
            score=0
    assert score is not None
    return(score)


# Everything that follows has to do with
# Chapter 3, Section 14, rule 4.

similarities={'b':'pv',
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
       'z':'js'}

def test_similarity(letter,pattern):
    if pattern=='.':
        return False
    return letter in pattern

def check_for_similarity(word, gismu_list):
    word=word.rstrip()
    pats = map(lambda x:similarities.get(x,'.'),word)
    gismu_list.seek(0)
    found=0
    for gismu in gismu_list:
        gismu=gismu.rstrip()
        if word[:4] == gismu[:4]:
            found=1
            break
        for i in xrange(5):
            if word[:i]==gismu[:i] and \
               word[i+1:]==gismu[i+1:] and \
               test_similarity(gismu[i],pats[i]):
                found=1
                break
        if found:
            break
    if not found:
        return True
    else:
        print >>sys.stderr, '%s conflicts with gismu %s'% (word, gismu)
        return False
