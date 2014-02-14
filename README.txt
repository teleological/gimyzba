
This is an implementation of the lojban gismu creation algorithm as described in
"The Complete Lojban Language", chapter 4, section 14.

This version is based on work by Arnt Richard Johansen, integrating mlpy's LCS
(longest common subsequence) algorithm for faster performance.

To generate scored gismu candidates, run the "gismu_score.py" program,
passing as arguments six phonetically lojbanized words from the following
languages (in order): Chinese, Hindi, English, Spanish, Russian, and Arabic.
The output (STDERR) of the program is a serialize ("pickled") sequence of
tuples which should be redirected into a file for further processing, e.g.:

  python gismu_score.py uan rakan ekspekt esper predpologa mulud > scores.data

The first time it is run, "gismu_score.py" creates a DBM database
("candidates.db") of all possible gismus. This database will be consulted
on subsequent executions.

To interpret the results of the "scores.data" file, feed it as input to
"gismu_best.py", e.g.:

  python gismu_best.py < scores.data

The scripts and modules in this implementation may be copied, modified,
and distributed under the terms of the GNU General Public License v3.
For details, see "LICENSE.txt".

