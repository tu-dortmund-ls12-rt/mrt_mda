# mrt_mda
Relation between MRT and MDA. (Evaluation)

Evaluation for the paper:

*On the Equivalence of Maximum Reaction Time and Maximum Data Age for Cause-Effect Chains*


This version only evaluates the End-to-end latency based on the MRT, without considering MDA, MRDA, or MRRT.

This evaluation uses python3.9.
Make virtual environment with 
```
python3.9 -m venv venv
```

Activate environment with 
```
source venv/bin/activate
```

Install requirements
```
pip3 install -r requirements. txt
```

Run experiments using 
```
python3 -O eval -s0 -p200 -r1000 -n10000
```
(```p``` is the number of concurrent processes and should be reduced to less than the number of available processors of the machine. 
```r``` and ```n``` can be reduced to run the experiments faster.)