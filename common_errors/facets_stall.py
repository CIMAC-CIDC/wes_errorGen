#!/usr/bin/env python

#Jacob Geisberg 8/2022
import argparse
import os
from pathlib import Path

def file_toucher(path):
    '''Touches a given path. Will create directories as needed.
    WILL TOUCH EXISTING FILES!
    '''
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        Path(path).touch()
        print('wrote: %s' %(path))
    else:
        Path(path).touch()
        print('touched: %s' %(path))

def main():
    parser = argparse.ArgumentParser(
    description="creates and touches files to allow pipeline to continue if facets stalls out")
    parser.add_argument("run", help="name of the run, usually tumor CIMAC ID")
    parser.add_argument("-d", "--directory", default="/mnt/ssd/wes/", help="path to wes results. deafult: /mnt/ssd/wes/analysis")
    args = parser.parse_args()
    if args.directory[-1] != "/":
        args.directory += "/"

    # THE ORDER OF FILES HERE IS VERY IMPORTANT!!
    lst = [
    'purity/{run id}/{run id}_purity_results.txt', #(should exist already)
    'purity/{run id}/{run id}_purity_postprocessed_results.txt', # (should exist already)
    'purity/{run id}/{run id}.optimalpurityvalue.txt',
    'purity/{run id}/{run id}.iterpurityvalues.txt',
    'purity/{run id}/{run id}.cncf',
    'purity/{run id}/{run id}_facets_gainLoss.bed', # I think we need to add actual stuff to this one
    ]

    for file in lst:
        file = args.directory + file.replace("{run id}", args.run)
        file_toucher(file)

    with open(file, "w") as f:
        f.write("chrom\tstart\tend\ttotal_cncall\n")

    #print




if __name__=='__main__':
    main()
