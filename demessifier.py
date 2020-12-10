
#!/usr/bin/python


"""
This script cleans up after making a slurmy mess
This script has two steps: arming and cleaning.
During the arming step, a directory is created for your run and
the files to clean are tracked. During the cleaning step, done after your pipeline,
the tracked files are moved to the dedicated directory.
"""

# imports
import click
import subprocess
import logging
from datetime import date
import os
import sys
import re


def welcome(command):
    print("Hoi.")
def findFiletypes(filelist):
    switch = {
    "gz":lambda x: (x.split(".")[-1] if len(x.split(".")) <= 2 else ".".join(x.split(".")[-2:])),
    "out" : lambda x: ("slurm" if re.search("slurm-.*\.out",x) else x.split(".")[-1]),
    "core": lambda x: (x.split(".")[0] if re.search("core.[0-9]*$",x) else x.split(".")[-1])
    }
    extensions = []
    for file in filelist:
        regex = "core.[0-9]*$"
        if re.search(regex,file):
            ext = "core"
        else:
            ext = file.split(".")[-1]
        extensions.append(switch.get(ext,lambda x: x.split(".")[-1])(file))
    return(list(set(extensions)))

def getRunName(outdir):
    today=date.today()
    default_name="demessifier_{}_{}_{}".format(today.year,today.month,today.day)
    okay = False
    count = 1
    outname = default_name 

    while True:
        if os.path.isdir("{}/{}".format(outdir,outname)):
            outname = "{}_{}".format(default_name,count)
            count += 1
        else:
            break
    return(outname)

            
   
def writeToFile(dir,name, present_files):
    filename = "demessifier_armed_{}.txt".format(name)
    snapshot = ",".join(present_files)
    message = "run_name:{}\ndir:{}\nsnapshot:{}".format(name,dir,snapshot)
    with open(filename,'w') as outfile:
        outfile.write(message)    

def goodbye(status):
    # Returns exit message
    ## TODO: add different actions for different exit statuses
    if status == 0:
	    print("Thanks for using Demessifier!")
    sys.exit()

# Add date and time to log messages
logging.basicConfig(
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M",
    format="[%(asctime)s %(levelname)s] %(message)s",
)

@click.group()
def cligroup():
    """
    #### IdentMGE ####                                                                                                                                                                                                                                                                                                                                                                                                                                                                        Identification of Mobile Genetic Elements in metagenomics samples.                                                                                                                                                                           """


@cligroup.command(
    "arm",
    short_help="Arm the script before cleaning up"
)

@click.option("-n",
    "--name",
    default=getRunName(dir),
    show_default=False,
    help="Give the run you want to log a name"
)

@click.option("-d",
    "--dir",
    default="./demessifier_logs",
    type=click.Path(dir_okay=True, writable=True),
    help="Location to put the files"
)

def arm_demessifier(name, dir):
    welcome("arm")
    # make output directory
    try:
        os.makedirs("{}/{}".format(dir,name))
    except FileExistsError:
        name = getRunName(dir)
       	print("Run name already exists in this directory. I'll use a generic name!\nYour files will be in {}/{}".format(dir,name))
        os.makedirs("{}/{}".format(dir,name))            

    # Make log of files that already exist
    # not really needed yet, because for now it could only copy all slurm files to the log dir
    # but at some point it might be useful to know which files have been generated since arming
    # e.g. when you want to add other log files that are generated, core files, intermediate files, etc.
    # I also plan to implement a "clean all" option, for which this is the first step.
    present_files = os.listdir(".")
    writeToFile(dir,name,present_files)

@cligroup.command("clean")
@click.option("-c","--cleaning",type=click.Choice(["slurm","full"],case_sensitive=False),default="slurm")
@click.option("-n","--name",required=True)
def clean(name,cleaning):
    welcome("clean")
    recover = open('demessifier_armed_{}.txt'.format(name),'r').read().splitlines()
    recov_list = [[x.split(':') for x in recover]]
    recov_dict = {}
    for entry in recov_list:
        recov_dict.update(dict(entry))
    name,dir,snapshot= "","",""
    try:
        name = recov_dict['run_name']
        dir = recov_dict['dir']
        snapshot = recov_dict['snapshot'].split(',')
    except KeyError:
        print('Something went wrong. Please make sure the demessifier_armed file was not changed after arming.')
        goodbye(1)

    current_files = os.listdir('.')
    newfiles = list(set(current_files) - set(snapshot))

    if cleaning == "slurm":
        filetypes = ["slurm","core"]

    else:
        filetypes = findFiletypes(newfiles)

    for type in filetypes:
        typedict = {
        "slurm": "slurm-.*out$",
        "core": "core.[0-9]*$",
        "default": ".{}$"
        }
        regex = typedict.get(type, typedict.get("default")).format(type)
        
        indices = [i for i,x in enumerate(newfiles) if re.search(regex,x)]
        print(type, regex, indices)
        try:
            os.makedirs("{}/{}/{}".format(dir,name,type))
        except FileExistsError:
            if os.path.exists("{}/{}/done.txt".format(dir,name)):
                print("It looks like this mess is cleaned already! Please check your given name or try arming a new experiment")
            else:
                print("It looks like something went wrong. Cleaning has failed. Please try arming a new experiment")
            goodbye(1)

        files = [newfiles[i] for i in indices]
        for file in files:
            os.rename("./{}".format(file), "{}/{}/{}/{}".format(dir,name,type,file))
    
    open('{}/{}/done.txt'.format(dir,name),'w').close()             
    goodbye(0)

@cligroup.command("test")
def test():
    testlist = ["a.txt","b.fasta","slurm-123489.out","123489.core","b.txt","c.fastq.gz","d.tar.gz","e.gz","blast.out","core.19827"]
    print(findFiletypes(testlist))
    a = "core.9843"
    print(re.search("core.[0-9]*$",a))
if __name__ == "__main__":
    cligroup()
