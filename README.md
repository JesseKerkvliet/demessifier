# Demessifier
This tool is designed to clean working directories that have been used to test or use pipelines, specifically using the Slurm job scheduler. The tool works in two stages:
## Arming
First, before running your pipelines, you need to arm the demessifier tool. This can be done by running
```
python demessifier.py arm --dir [output dir] --name [run name]
```
This will generate the necessary output directory and create a snapshot of the files in the working directory.

## Cleaning
Second, after running your pipelines, you can clean the armed run by running:
```
python demessifier.py clean --cleaning [slurm or full] --name [run name]
```
Depending on the cleaning level (slurm or full for now), the tool will move the generated files to the output directory. Every file extension gets a separate directory.
Slurm cleaning level only moves the core.[jobid] and slurm-[jobid].out files that are generated. Full cleaning level moves all files that have been generated since the arming of the job to the specified directory.

## Requirements
The tool only requires Python 3.8 and the python library Click (available on pip)
 

