FSMT unit tests
============================================================

This section is a short gathered description of all included unit tests on the 
entire FSMT application. It consists of simple ``iniparsing`` tests and 
``launch_tests`` which are running ``fsmt``, specifically testing observers.


Test Matrix
-------------------------------------------------------------------------------------
==========  ==========  ==========    ==========  ==========
PID          STDOUT     STDEXCLUDE    LOCKFILE    test
==========  ==========  ==========    ==========  ========== 
  -/-         -/-         -/-           -/-       launchtest_seq_0

  Y/Y         -/-         -/-           -/-       launchtest_seq_2, ``!launchtest_seq_7``
  Y/N         -/-         -/-           -/-       launchtest_seq_12, launchtest_seq_13
  N/Y         -/-         -/-           -/-       launchtest_seq_1
  N/N         -/-         -/-           -/-       launchtest_seq_16 (somewhat useless)
\
  -/-         Y/Y         -/-           -/-       ``!launchtest_seq_7``
  -/-         Y/N         -/-           -/-       launchtest_seq_3
  -/-         N/Y         -/-           -/-       **TODO**
  -/-         N/N         -/-           -/-       launchtest_seq_4
\
  N/N         N/N         Y/Y           N/N       **TODO**
  N/N         N/N         Y/N           N/N       **TODO**
  N/N         N/N         N/Y           N/N       **TODO**
\
  -/-         -/-         -/-           Y/Y       **TODO**
  -/-         -/-         -/-           Y/N       launchtest_seq_9, launchtest_seq_10, launchtest_seq_11
  -/-         -/-         -/-           N/Y       **TODO**
  -/-         -/-         -/-           N/N       **TODO**
\
  N/N         N/N         -/-           -/-       launchtest_seq_5
  Y/N         Y/N         -/-           -/-       launchtest_seq_6, launchtest_seq_7, launchtest_seq_8, launchtest_seq_9, launchtest_seq_15
  Y/N         N/N         -/-           -/-       launchtest_seq_14
  Y/N         -/-         Y/N           -/-       launchtest_seq_10, launchtest_seq_11
  Y/N         -/-         Y/Y           -/-       launchtest_seq_12
  Y/N         -/-         -/-           Y/N       launchtest_seq_15
  -/-         Y/N         -/-           Y/N       launchtest_seq_15
  Y/N         Y/N         -/-           Y/N       launchtest_seq_15    
==========  ==========  ==========    ==========  ==========

**Notation**: 
	``Y/N`` tuple = ``blocking/ongoing`` tuple
	
	``Y`` = yes
	
	``N`` = no
	
	``-`` = unused

	``!testname`` = this is a negative test, meaning it provokes an 
	unstatisfied criteria on purpose to test the observers



INI parsing tests
----------------------------------------------------------

Iniparsertest cfg 1 (sequential + parallel)
    - converts to a test scxml that launches 2 components
    - components: xeyes, gnome-calculator
    - Uses: pid (blocking + not ongoing)
    - tested sequence: (('a','b',),[('a',),('b',)])

Iniparsertest cfg 2 (parallel)
    - converts to a test scxml that launches 2 components
    - components: xeyes, gnome-calculator
    - Uses: pid (blocking + not ongoing)
    - tested sequence: ([('a',),('b',)],)

Iniparsertest cfg 3 (sequential + parallel + sequential)
    - converts to a test scxml that launches 2 components
    - components: xeyes, gnome-calculator
    - Uses: pid (blocking + not ongoing)
    - tested sequence: ('a',),[('a',),('b',)],('b',)

Iniparsertest cfg 4 (sequential + parallel[sequential & single] + sequential)
    - converts to a test scxml that launches 2 components
    - components: xeyes, gnome-calculator
    - Uses: pid (blocking + not ongoing)
    - tested sequence: ('a',),[('a','b'),('a',)],('b',)


FSMT launch tests
----------------------------------------------------------

Launchtest seq 1 (pid test)
    - launch two components sequentially and close them properly
    - components: 2x fsmt_exsilent
    - Uses: pid (not blocking + ongoing)

Launchtest seq 2 (pid test)
    - launch two components sequentially and close them properly
    - components: 2x fsmt_exsilent
    - Uses: pid (blocking + ongoing)

Launchtest seq 3 (stdout test)
    - launch two components sequentially and close them properly
    - components: 2x fsmt_exouttimed
    - Uses: stdout (blocking + not ongoing)

Launchtest seq 4 (stdout test)
    - launch two components sequentially and close them properly
    - components: 2x fsmt_exouttimed
    - Uses: stdout (not blocking + not ongoing)

Launchtest seq 5 (stdout+pid test)
    - launch two components sequentially and close them properly
    - components: 2x fsmt_exouttimed
    - Uses: stdout (not blocking + not ongoing)
            pid (not blocking + not ongoing)

Launchtest seq 6 (stdout+pid test)
    - launch two components sequentially and close them properly
    - components: 2x fsmt_exouttimed
    - Uses: stdout (blocking + not ongoing)
            pid (blocking + not ongoing)

Launchtest seq 7 (NEGATIVE pid endless ongoing mode test)
    - launch two components sequentially and close them properly
    - components: 2x fsmt_exouttimed
    - Uses: stdout (blocking + not ongoing)
            pid (blocking + ongoing)

Launchtest seq 8 (stdout ongoing warning + pid test)
    - launch two components sequentially and close them properly
    - components: 2x fsmt_exouttimed
    - Uses: stdout (blocking + ongoing)
            stdout (blocking + not ongoing)
            pid (blocking + not ongoing)

Launchtest seq 9 (lockfile test)
    - launch two components sequentially and close them properly
    - components: fsmt_exsilent, fsmt_exouttimed
    - Uses: lockfile (blocking + ongoing)
            stdout (blocking + not ongoing)
            pid (blocking + not ongoing)

Launchtest seq 10 (stdoutexclude test)
    - launch two components sequentially and close them properly
    - components: fsmt_exsilent, fsmt_exouttimed
    - Uses: lockfile (blocking + not ongoing)
            pid (blocking + not ongoing)
            stdoutexclude (blocking + not ongoing)

Launchtest seq 11 (NEGATIVE stdoutexclude test)
    - launch two components sequentially and close them properly
    - components: fsmt_exsilent, fsmt_exouttimed
    - Uses: lockfile (blocking + not ongoing)
            pid (blocking + not ongoing)
            stdoutexclude (blocking + not ongoing)

Launchtest seq 12 (stdoutexclude ongoing test)
    - launch two components sequentially and close them properly
    - components: 2x fsmt_exouttimed
    - Uses: pid (blocking + not ongoing)
            stdoutexclude (blocking + ongoing)

Launchtest seq 13 (reverse kill)
    - launch 6 components sequentially and close them properly
    - components: 6x fsmt_exsilent
    - Uses: pid (blocking + not ongoing)

Launchtest seq 14 (kill component after wait even though stdout is not finished)
    - launch 2 components sequentially and close them properly
    - components: 2x fsmt_exouttimed
    - Uses: pid (blocking + not ongoing)
            stdout (not blocking + not ongoing)

Launchtest seq 15 (stdout blocking feature test)
    - launch 4 components sequentially and close them properly
    - components: fsmt_exlockouttimed
    - Uses: pid (blocking + not ongoing), lockfile (blocking + not ongoing), stdout (blocking + not ongoing)


