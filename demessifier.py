
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
        outfile.write()    

def goodbye():
    # Returns exit message
    print("Thanks for using Demessifier!")

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
    # make output directory
    print("{}/{}/".format(dir,name))
    try:
        os.makedirs("{}/{}".format(dir,name))
    except FileExistsError:
        name = getRunName(dir)
        print(name)
       	print("Run name already exists in this directory. I'll use a generic name!\nYour files will be in {}/{}".format(dir,name))
        os.makedirs("{}/{}".format(dir,name))            

    # Make log of files that already exist
    # not really needed yet, because for now it could only copy all slurm files to the log dir
    # but at some point it might be useful to know which files have been generated since arming
    # e.g. when you want to add other log files that are generated, core files, intermediate files, etc.
    # I also plan to implement a "clean all" option, for which this is the first step.
     
    present_file = os.listdir(".")
    writeToFile(dir,name,present_files)

@cligroup.command("clean")
@click.option("-c","--cleaning",type=click.Choice(["slurm","full"],case_sensitive=False),default="slurm")
@click.option("-n","--name",required=True)
def clean(name,cleaning):
    print("cleaning goes here")
    recover = open('demessifier_armed_{}.txt'.format(name),'r').read().splitlines()
    recov_list = [[x.split(':') for x in recover]]
    recov_dict = {}
    for entry in recov_list:
        recov_dict.update(dict(entry))

    print(recov_dict)
    try:
        name = recov_dict['rune_name']
        dir = recov_dict['dir']
        snapshot = recov_dict['snapshot'].split(',')
    except KeyError:
        print('somethings wrong')
    print(snapshot)

    current_files = os.listdir('.')
    newfiles = list(set(current_files) - set(snapshot))
    print(newfiles)
    if cleaning == "slurm":
        indices = [i for i, x in enumerate(newfiles) if x.find("slurm-") != -1 or x.find("core.")!= -1]
        to_clean = [newfiles[i] for i in indices]
    os.makedirs("{}/{}/slurm".format(dir,name))
    os.makedirs("{}/{}/core".format(dir,name))
    for file in to_clean:
        print(file)
        os.rename("./{}".format(file), "{}/{}/slurm/{}".format(dir,name,file))
 
                 
    print(to_clean)
if __name__ == "__main__":
    cligroup()
