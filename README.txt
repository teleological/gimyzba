
This is an implementation of the lojban gismu creation algorithm as
described in "The Complete Lojban Language", chapter 4, section 14.

The current version is based on work by Arnt Richard Johansen, integrating
a pure python implementation of the LCS (longest common subsequence)
algorithm for easy installation and optimal performance.

USAGE
=====

To generate scored gismu candidates, run the "gismu_score.py" program,
passing as arguments phonetically lojbanized words.

  python gismu_score.py uan rakan ekspekt esper predpologa mulud

The top ten highest scoring candidates will be displayed. Candidates
are scored according to resemblance to the input words, with additional
consideration given to languages which are more widely spoken in the
world. The default languages and and weighting factors, as derived from
the 1995 Encyclopedia Brittanica Book of the Year, are:

    Chinese     0.347
    Hindi       0.196
    English     0.160
    Spanish     0.123
    Russian     0.089
    Arabic      0.085

OPTIONS
=======

You may pass options to gismu_score.py to modify the way that gismu candidates
are generated and scored.

The --all-letters (-a) option generates candidates using all letters in the
lojban alphabet, whether or not they appear in the input words. This has the
effect of requiring substantially more processing time to generate scores.

The --weights (-w) option controls the language weights, accepting a
comma-separated list of weights, or alternately, a year for which lojban
language weights were published. Years currently supported: 1985, 1987,
1994, 1995 (default), and 1999.

The --shapes (-s) option enables you to experiment with different gismu
"shapes". Pass a comma-separated list of shapes, described with "c"
for consonant and "v" for vowel. The default value for this option is
"ccvcv,cvccv".

The --number-workers (-n) option controls the number of python scoring threads
to use. This may only be useful with python implementations which don't use
a GIL (Global Interpreter Lock) such as jython.

The --deduplicate (-d) option accepts a path to file containing a list of
pre-existing gismu, one per line (e.g "gismu-list.txt"). Candidates will be
matched against the gismu in this file; candidates that are deemed similar
to existing gismu will be disqualified.

The --output (-o) option accepts a filepath. All candidates, along with their
scores will be written to this path. The format is serialized ("marshaled")
tuples, and may be passed as input to "gismu_best.py", e.g.:

  python gismu_best.py < scores.data

The --quiet (-q) option suppresses the display of progress while scores
are being calculated.

CHANGES
=======

See "CHANGELOG.txt".

LICENSE
=======

The scripts and modules in this implementation may be copied, modified,
and distributed under the terms of the GNU General Public License v3.
For details, see "LICENSE.txt".

"gismu-list.txt" contains public domain content furnished by:

  Logical Language Group, Inc.
  2904 Beau Lane
  Fairfax, VA 22031
  USA

