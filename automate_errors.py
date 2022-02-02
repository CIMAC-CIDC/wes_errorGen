#!/usr/bin/env python
'''Jacob Geisberg Jan,2022
This script generates all of the missing files required for ingestion
of errored runs based on user input of which modules have failed and their
error codes.'''

import requests
import json
import os
import sys
import argparse
import yaml
from pathlib import Path

#helpers
def create_dict(id, modules, TO, tumor, normal=None):
    '''Takes the run id, errored modules, tumor id, and normal id and
    generates a dictionary of each module and which files must be written.
    '''

    # read raw json API file from github repo
    url = 'https://raw.githubusercontent.com/CIMAC-CIDC/cidc-ngs-pipeline-api/master/cidc_ngs_pipeline_api/wes/wes_output_API.json'
    file = requests.get(url)
    file = file.json()


    dict = {}
    # the API has run id, tumor cimac id, and normal cimac id sections.
    # this dictionary provides a way to translate them into our variables.
    wildcards = {"run id": id,
                 "tumor cimac id": tumor,
                 "normal cimac id": normal}

    # run through each file in the API and add it to the output dictionary
    for wildcard in file.keys():
        if not ((wildcard == "normal cimac id") and TO == True): # dont make normal sample files for TO runs. API may need fixing
            for f in file[wildcard]:
                path = f['file_path_template']
                module = path.split("/")[1] #second directory in path is always module name
                file_TO = f['tumor_only_assay']
                optional = f['optional']
                exclude = TO and (not file_TO)#ensures that no normal files are included for TO samples
                if (not optional) and (module in modules) and (not exclude):
                    path = path.replace('{'+ wildcard +'}', wildcards[wildcard])
                    if module in dict:
                        dict[module].append(path)
                    else:
                        dict[module] = [path]
    return dict


def file_writer(path):
    '''Writes text to a given path. Will create directories as needed.
    '''
    #overwrite existing file
    if os.path.exists(path):
        print("File already exists: %s " %(path))

    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        Path(path).touch()
        print('wrote: %s' %(path))




def create_yaml(run_name, file_dict, code_nums):
    '''Taking a dictionary of files and a dictionary of error codes for each file,
    it will create an error.yaml file.
    '''

    #UPGRADE TO BETTER INPUT FOR ERROR STRINGS
    code_strings={
    '00': 'Unknown error',
    '01': 'Data file corrupt or unreadable',
    '02': 'PE reads incorrectly paired',
    '03': 'Poor read quality',
    '04': 'Too few reads',
    '05': 'Duplicate normal sample -- not used for analysis',
    '11': 'External software bug/issue {software: XXX}',
    '12': 'WES pipeline software bug/issue {module: XXX}',
    '21': 'Out of disk space error',
    '22': 'Out of memory error',
    '23': 'Unexpected interruption of service',
    '30': 'Did not finish computation after 6 hours'
    }

    # Itterates through the file dictionary to create yaml entries for each file
    dict = {"errors":{}} # stores the yaml entries for each file
    for module in file_dict:
        code_num = code_nums[module]

        # checks that user error numbers are valid
        if code_num not in code_strings:
            print('Please make sure all error codes are valid and try again.')
            sys.exit(-1)

        # 11 requires a software field that should be provided once
        if code_num == "11":
            software = input("Please enter errored software for %s: " % (module))

        # generates appropriate entry for each file based on error code
        for file in file_dict[module]:
            message = "ERROR%s: %s" % (code_num,code_strings[code_num])
            # 11 and 12 are special cases that require string replacement
            if code_nums[module] == "11":
                message = message.replace("XXX", software)
            elif code_nums[module] == "12":
                message = message.replace("XXX", module)
            dict['errors'][file] = message

    path = "analysis/%s_error.yaml" % (run_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)# in case analysis folder doesn't yet exist
    with open(path, "w") as outfile:
        yaml.dump(dict, outfile, width=float("inf"), sort_keys=True)
    print("successfully wrote yaml to: %s" % (path))



#main function
def main():

    parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter, # keep newlines
    description="Simply add name of the setup yaml and the corresponding error code for each failed module \nex. -n 30 -c 21 \n",
    epilog= "error codes:\n"
    '00: Unknown error\n'
    '01: Data file corrupt or unreadable\n'
    '02: PE reads incorrectly paired\n'
    '03: Poor read quality\n'
    '04: Too few reads\n'
    '05: Duplicate normal sample -- not used for analysis\n'
    '11: External software bug/issue {software: XXX}\n'
    '12: WES pipeline software bug/issue {module: XXX}\n'
    '21: Out of disk space error\n'
    '22: Out of memory error\n'
    '23: Unexpected interruption of service\n'
    '30: Did not finish computation after 6 hours\n')

    parser.add_argument("yaml", help="(REQUIRED) name of the yaml used to generate the instance")
    parser.add_argument("-a", "--align", help="align module error code")
    parser.add_argument("-c", "--clonality", help="clonality error code")
    parser.add_argument("-d", "--copynumber", help="copynumber error code")
    parser.add_argument("-e", "--coverage", help="coverage error code")
    parser.add_argument("-g", "--germline", help="germline error code")
    parser.add_argument("-m", "--metrics", help="metrics error code")
    parser.add_argument("-q", "--missensor2", help="missensor2 error code")
    parser.add_argument("-n", "--neoantigen", help="neoantigen error code")
    parser.add_argument("-o", "--optitype", help="optitype error code")
    parser.add_argument("-p", "--purity", help="purity error code")
    parser.add_argument("-r", "--report", help="report error code")
    parser.add_argument("-u", "--rna", help="rna error code")
    parser.add_argument("-s", "--somatic", help="somatic error code")
    parser.add_argument("-t", "--tcellextrect", help="tcellextrect error code")
    parser.add_argument("-x", "--xhla", help="xhla error code")
    args = parser.parse_args()
    codes_dict = vars(args)
    codes_dict = {key: value for (key, value) in codes_dict.items() if value is not None}
    config_yaml_path = codes_dict.pop("yaml") # config_yaml_path is not a module and should be stored separately
    modules = [x for x in codes_dict]

    # open yaml file
    with open(config_yaml_path, "r") as config_file:
        try:
            config_dict = yaml.safe_load(config_file)

        except yaml.YAMLError as error:
            print(error)

    #interpret yaml to get run, tumor, and normal ids
    samples = config_dict["metasheet"]
    run_name = list(samples)[0]
    tumor = samples[run_name]["tumor"]
    if "normal" in samples[run_name].keys():
        normal = samples[run_name]['normal']
        TO = False
    else:
        normal = None
        TO = True


    file_dict = create_dict(run_name, modules,TO,tumor,normal)
    create_yaml(run_name, file_dict, codes_dict)
    for module in file_dict:
        for file in file_dict[module]:
            file_writer(file)


if __name__=='__main__':
    main()
