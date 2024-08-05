# Partitioned Job Chain 

Evaluation for the paper:

*On the Equivalence of Maximum Reaction Time and Maximum Data Age for Cause-Effect Chains*

This version evaluates the speedup obtained by partitioned job chains regarding the end-to-end latency based on the MRT---without considering MDA, MRDA, or MRRT.

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
python3 -O eval -s0 -p200 -r10000 -n10000
```
(```p``` is the number of concurrent processes and should be reduced to less than the number of available processors of the machine. 
```r``` and ```n``` can be reduced to run the experiments faster.)
On our machine, the experiments take less than 10 minutes total, using the command above.

Note: The file ```output240805.zip``` contains the evaluation results obtained on 5th of August, 2024.