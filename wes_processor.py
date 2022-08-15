#!/usr/bin/env python

#Jacob Geisberg 8/2022
import pydot
import pandas as pd
import requests
import json
import os
import sys
import argparse
import yaml
from pathlib import Path
import subprocess
#from collections import deque

code_prompt= ("error codes:\n"
'00: Unknown error\n'
'01: Data file corrupt or unreadable\n'
'02: PE reads incorrectly paired\n'
'03: Poor read quality\n'
'04: Too few reads\n'
'05: Duplicate normal sample -- not used for analysis\n'
'11: External software bug/issue {software: XXX}\n'
'12: WES pipeline software bug/issue {module: XXX}\n'
'13: Upstream module bug/issue {module: XXX}\n'
'21: Out of disk space error\n'
'22: Out of memory error\n'
'23: Unexpected interruption of service\n'
'30: Did not finish computation after 6 hours\n')

codes={
    '00': 'Unknown error',
    '01': 'Data file corrupt or unreadable',
    '02': 'PE reads incorrectly paired',
    '03': 'Poor read quality',
    '04': 'Too few reads',
    '05': 'Duplicate normal sample -- not used for analysis',
    '11': 'External software bug/issue {software: XXX}',
    '12': 'WES pipeline software bug/issue {module: XXX}',
    '13': 'Upstream module bug/issue {module: XXX}',
    '21': 'Out of disk space error',
    '22': 'Out of memory error',
    '23': 'Unexpected interruption of service',
    '30': 'Did not finish computation after 6 hours'
    }

def get_downstream(node, nodes):
    '''takes a job ID and identifies downstream job IDs, including self, effectively a BFS'''
    downstream = [i for i in nodes[node]]
    downstream.append(node) # WE NEED TO HANDLE BROKEN RULE TOO!
    queue = [i for i in nodes[node]]
    while queue:
        n = queue.pop()
        downstream.append(n)# we will get unique values later
        if n in nodes: # check if node has children since some rules are endpoints
            children=nodes[n]
            for child in children:
                if child not in queue:
                    queue.append(child)
    return list(set(downstream))




def get_node_files(node, graph, files):
    '''takes a job number, job graph, and job to file dataframe and returns a list
    of the files prodcued by the job. '''

    n = graph.get_node(node)[0]
    label=n.get("label").split("\\n")[0].strip('\"')
    f=files.loc[files['rule'] == label, ['output_file']] #match label of job to rule in files
    f=f.output_file.to_list()
    return f

def get_ingested_files(id, TO, tumor, normal=None):
    '''Pulls all possible ingested files from dropbox and returns the names of all
    files needed for the run based on runID and tunor and normal names. This list
    includes files that have already been sucessfully run.'''

    print("getting ingetsed files")

    #PULLING FILES FROM DROPBOX
    url = 'https://raw.githubusercontent.com/CIMAC-CIDC/cidc-ngs-pipeline-api/master/cidc_ngs_pipeline_api/wes/wes_output_API.json'
    files = requests.get(url)
    files = files.json()
    wildcards = {"run id": id,
                 "tumor cimac id": tumor,
                 "normal cimac id": normal}

    # COMPILING RELEVANT FILE NAMES BASED ON SUPPLIED NAMES AND DATA
    lst=[]
    for wildcard in files.keys(): # API is split by run_id, tumor and normal files
        if not ((wildcard == "normal cimac id") and TO == True): # dont make normal sample files for TO runs. API may need fixing
            for file in files[wildcard]:
                path = file['file_path_template']
                file_TO = file['tumor_only_assay']
                optional = file['optional']
                exclude = TO and (not file_TO)#ensures that no normal files are included for TO samples
                path = path.replace('{'+ wildcard +'}', wildcards[wildcard])
                if (not optional) and (not exclude):
                    lst.append(path)
    return lst

def file_writer(path):
    '''Writes text to a given path. Will create directories as needed.
    DOES NOT OVERWITE EXISTING FILES!
    '''

    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        Path(path).touch()
        print('wrote: %s' %(path))
        # # for testing purposes only
        # with open(path, "w") as f:
        #     f.write("I am Jason Bourne")




def main():
    parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter, # keep newlines
    description="Finds all affected files from a given error, generates blank files that are needed for ingestion, and allows easy construction of error.yaml",
    epilog="")
    group = parser.add_mutually_exclusive_group(required=True)
    #dryrun here?
    group.add_argument("-r", "--rule", help="name of the rule that errored out")
    group.add_argument("-f", "--file", help="name of the output file that errored out")
    group.add_argument("-j", "--job", help="job id number that errored out")
    parser.add_argument("--folder", default="/mnt/ssd/wes/", help="location of WES results")# should it be /mnt/ssd/wes/analysis?
    parser.add_argument("-d", "--dag", default="sample_dag.dot", help="file containing a complete dag of the run. can be generated with: snakemake -s cidc_wes/wes.snakefile --forceall -n --dag > sample_dag.dot")
    # does not relate rules to missing files so should not be set right now
    #parser.add_argument("-t", "--tsv", default="summary.tsv", help="file conatining summary of all files in a  workflow")
    parser.add_argument("-m", "--metasheet", default="metasheet.csv", help="name of the metasheet used")
    parser.add_argument("-t", "--tumor_only", default=False, help="whether the sample was run with a matched normal")
    args = parser.parse_args()
    argument_dict = vars(args) #needed?
    print(argument_dict)

    #CREATE JOB GRAPH AND FILE TO RULE TABLE
    graph = pydot.graph_from_dot_file(args.dag)
    graph=graph[0]
    nodes={}
    for edge in graph.get_edge_list():
        source=edge.get_source()
        destination=edge.get_destination()
        if source not in nodes:
            nodes[source]=[destination]
        else:
            nodes[source].append(destination)

    files=pd.read_csv("summary.tsv", header=1, delimiter="\t")

    #GET RUN, TUMOR AND NORMAL NAMES
    samples=pd.read_csv(args.folder + "/" + args.metasheet, header=15).loc[0]#pandas does not seem to like out metasheet
    run_name = samples["RunName"]
    tumor = samples["Tumor"]
    normal = samples["Normal"]

    #HANDLE TUMOR ONLY HERE!!!!!! WE MIGHT NEED TO CHANGE THE DAG AS WELL...
    # if "normal" in samples[run_name].keys():
    #     normal = samples[run_name]['normal']
    #     TO = False
    # else:
    #     normal = None
    #     TO = True


    #GET DOWNSTREAM MODULES AND FILES (RIGHT NOW ONLY JOBID IS SUPPORTED)
    #SOME PSEUDO-CODE HERE FOR ALTERNATIVE INPUTS
    #if rule loop over nodes in dag and return job of rule in # qeustion
    # if file, parse file, get rule, get job
    #print(args.job)
    downstream_jobs=get_downstream(args.job, nodes)
    print(downstream_jobs)
    downstream_files = []
    for job in downstream_jobs:
        downstream_files += get_node_files(job, graph, files)

    #CONVERT FILES INTO PROPER NAMES BASED ON METASHEET
    print("old:", downstream_files)
    for i in range(len(downstream_files)):
        downstream_files[i] = downstream_files[i].replace("RUN", run_name)
        downstream_files[i] = downstream_files[i].replace("TUMOR", tumor)
        downstream_files[i] = downstream_files[i].replace("NORMAL", normal)
        downstream_files[i]
    print()
    print("new:", downstream_files)





    #GET INGESTED FILES FROM CIDC API AND INTERSECT WITH DOWNSTREAM FILES
    ingested_files=get_ingested_files(run_name, args.tumor_only, tumor, normal)
    #APPLY TRANSFORMATION HERE IF summary tsv/dag AND METASHEET DON'T MATCH


    affected_files=sorted([x for x in downstream_files if x in ingested_files])

    #HANDLE EACH FILE
    yaml_dict = {"errors":{}}
    previous=""
    for file in affected_files:

        #DETERMINE ABSOLUTE FILE PATH
        if args.folder[-1] == "/": #maybe check and modify arg.folder earlier to ensure that it has a trailing "/"
            path = args.folder + file
        else:
            path = args.folder + "/" + file
        print(path)

        #ADD FILE STATUS TO HELP THE USER
        #file_status=""
        if not os.path.exists(path):
            print("file status: missing")
            file_writer(path) # we create missing files for ingestion

        elif os.path.getsize(path) == 0:
            print("file status: empty")

        #add condition here to handle unhealthy looking file

        else:
            print("file status: uncertain")
            #if file is not empty, we add a preview
            print("file_preview:")
            subprocess.run("head -n 5 %s" % (path), shell=True)
            print()
            # if os.path.exists(path):
            #     print("file_preview:")
            #     subprocess.run("head -n 5 %s" % (path), shell=True)
            #     print()


        #GETTING ERROR CODE FROM USER
        valid=False
        while not valid:
            error_code = input("Enter a valid error code. Press 'e' to view error codes, f to view file_path, and 'ENTER' to add no error: ")
            if error_code == "":
                valid = True
                print("no error for %s" % path)
            elif error_code == "e":
                print(code_prompt)
            elif error_code == "f":
                print(file)
            elif error_code not in codes:
                print('Error code invalid. Please try again!')
            else:
                valid = True
                if error_code in ["11","12","13"]:
                    if error_code == "11":
                        prompt = "Please enter errored software for the file: "
                    elif error_code == '12':
                        prompt = "Please enter errored module for the file: "
                    else:
                        prompt = "Please enter the upstream module error for the file: "
                        # possibly include autocomplete or memory function here but there are downsides
                    txt =  input(prompt)

                #ADDING ERROR MESSAGE TO OUTPUT DICTIONARY
                message = "ERROR%s: %s" % (error_code, codes[error_code])
                if error_code in ["11","12","13"]:
                    message = message.replace("XXX", txt)
                yaml_dict['errors'][file] = [{"error": message}]
                print(file + ':', yaml_dict['errors'][file]) # testing code


        #TAKING COMMENTS FROM THE USER
        valid = False
        while not valid:
            comment = input("Enter a comment, press 'p' to repeat previous comment, or press 'Enter' to skip: ")
            if comment == '':
                valid =True
            else:
                if comment == "p":
                    comment = previous
                response=input("You are about to add '%s' as a comment to %s. Is this ok (y/n)" % (comment, file))
                if response == "y":
                    valid = True
                    previous = comment

                    #ADDING COMMENT TO OUTPUT DICTIONARY
                    if file in yaml_dict['errors']:
                        yaml_dict['errors'][file].append({"comments": comment})
                    else:
                        yaml_dict['errors'][file]=[{"comments": comment}]
        print()# for spacing


    #WRITE YAML
    p = args.folder + '/' + "analysis/%s_error.yaml" % (run_name)
    with open(p, "w") as outfile:
        yaml.dump(yaml_dict, outfile, width=float("inf"), sort_keys=True)

    print("successfully wrote yaml to: %s" % (p))


if __name__=='__main__':
    main()
