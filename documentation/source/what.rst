What is FSMTest
================
Introduction
--------------------------------------------
Robot simulators, like the MORSE project, provide a safe and readily available environment for robot system testing,
reducing the effort for testing drastically. In principle, simulation testing is automatable, and thus a good target
for **Continuous Integration (CI)** testing. However, so far, high-level scenario tests still require complex component
setup and configuration before they can be run in the simulator. An added complication is, that there is no standard
for starting, configuring, or monitoring software components on todays robots.
Often, high-level tests are carried out manually, implementing a tailored solution, e.g, via shell scripts or launch
files, for a specific system setup. Besides the effort of manual execution and supervision, current tests mostly do not
take timing and orchestration, i.e., required process start-up sequence, into account. Furthermore, successful execution
of components is not verified, which might lead to subsequent errors during the execution chain. Most importantly, all
this knowledge about the test and its environment is implicit, often hidden in the actual implementation of the tailored
test suite.

To overcome these issues, this contribution introduces **a generic and configurable state-machine based process** 
(finite-state-machine testing, or short ``fsmt``) to automate 
   a) environment setup, 
   b) system bootstrapping, 
   c) system tests, 
   d) result assessment, and 
   e) exit and clean-up strategy. 
   
We have chosen a state-based approach in order to inherit a well structured automaton, which enables us to
invoke the steps mentioned above, in the desired order, and to explicitly model required test steps. Furthermore, the
state-chart model enables us to invoke states in parallel, or sequentially, which also makes orchestration, e.g.,
start-up of system components, feasible and most importantly controllable. Last but not least, errors during the
execution will prematurely end the state-machine to prevent subsequent errors.

Further Information, Talks, and Papers
--------------------------------------------
You can find additional information about FSMT here:

 * `International MORSE workshop paper 2013 <http://pub.uni-bielefeld.de/luur/download?func=downloadFile&recordOId=2602725&fileOId=2602726>`_
 * `International MORSE workshop talk 2013 <https://vimeo.com/68862135>`_
 * `International MORSE workshop slides 2013 <http://www.slideshare.net/FlorianLier/imw-20131>`_