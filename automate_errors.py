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
def create_dict(id, TO, tumor, normal=None):
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
                module = path.split("/")[1] #second directory in path is module name (for our purposes)
                file_TO = f['tumor_only_assay']
                optional = f['optional']
                exclude = TO and (not file_TO)#ensures that no normal files are included for TO samples
                #if (not optional) and (module in modules) and (not exclude):
                path = path.replace('{'+ wildcard +'}', wildcards[wildcard])
                if (not optional) and (not exclude):
                    # if os.path.exists(path):
                    #     if os.path.getsize(path) != 0:
                    #         break
                    # ADD TO DCITIONARY IF FILE IS ABSENT OR HAS SIZE 0
                    if not os.path.exists(path):
                        write= True
                    elif os.path.getsize(path) == 0: # checked separately due to missing file error
                        write=True
                    else:
                        write=False

                    if write==True:
                        if module in dict:
                            dict[module].append(path)
                        else:
                            dict[module] = [path]


    #print(dict)
    return dict



def file_writer(path):
    '''Writes text to a given path. Will create directories as needed.
    DOES NOT OVERWITE EXISTING FILES!
    '''
    #overwrite existing file
    # if os.path.exists(path):
    #     print("File already exists: %s " %(path))

    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        Path(path).touch()
        print('wrote: %s' %(path))
        # # for testing purposes only
        # with open(path, "w") as f:
        #     f.write("I am Jason Bourne")

    elif os.path.getsize(path) == 0:
        print('existing blank file: %s' %(path))





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
    '13': 'Upstream module bug/issue {module: XXX}',
    '21': 'Out of disk space error',
    '22': 'Out of memory error',
    '23': 'Unexpected interruption of service',
    '30': 'Did not finish computation after 6 hours'
    }

    # Itterates through the file dictionary to create yaml entries for each file
    dict = {"errors":{}} # stores the yaml entries for each file
    for module in file_dict:

        # adds error codes for cases when user has defined them
        if module in code_nums:
            code_num = code_nums[module]
            # checks that user error numbers are valid
            if code_num not in code_strings:
                print('Please make sure all error codes are valid and try again.')
                sys.exit(-1)

            # adds input prompts for error codes that require additional input
            elif code_num in ["11","12","13"]:
                if code_num == "11":
                    prompt = "Please enter errored software for %s: " % (module)
                elif code_num == '12':
                    prompt = "Please enter errored module for the %s folder: " % (module)
                else:
                    prompt = "Please enter upstream module error for %s: " % (module)
                txt =  input(prompt)

            # generates appropriate entry for each file based on error code
            for file in file_dict[module]:
                message = "ERROR%s: %s" % (code_num,code_strings[code_num])
                if code_num in ["11","12","13"]:
                    message = message.replace("XXX", txt)
                dict['errors'][file] = message


        #add files that do not have error code_strings
        else:
            for file in file_dict[module]:
                dict['errors'][file] = "ERROR CODE REQUIRED!"



    path = "analysis/%s_error.yaml" % (run_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)# in case analysis folder doesn't yet exist
    with open(path, "w") as outfile:
        yaml.dump(dict, outfile, width=float("inf"), sort_keys=True)
    print("successfully wrote yaml to: %s" % (path))



#main function
def main():

    parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter, # keep newlines
    description="Simply add name of the wes_automator yaml and the corresponding error code for each failed module \nex. ./automate_errors.py -n 30 -c 21 \n",
    epilog= "error codes:\n"
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

    parser.add_argument("yaml", help="(REQUIRED) name of the yaml used to generate the instance")
    parser.add_argument("-a", "--align", help="align module error code")
    parser.add_argument("-c", "--clonality", help="clonality error code")
    parser.add_argument("-d", "--cnvkit", help="cnvkit error code")# new in WESv3
    parser.add_argument("-e", "--copynumber", help="copynumber error code")
    parser.add_argument("-f", "--coverage", help="coverage error code")
    parser.add_argument("-g", "--germline", help="germline error code")
    parser.add_argument("-i", "--hlahd", help="hlahd error code") # new in WESv3
    parser.add_argument("-m", "--metrics", help="metrics error code")
    parser.add_argument("-q", "--missensor2", help="missensor2 error code")
    parser.add_argument("-n", "--neoantigen", help="neoantigen error code")
    parser.add_argument("-o", "--optitype", help="optitype error code")
    parser.add_argument("-p", "--purity", help="purity error code")
    #DO WE NEED RECALIBRATION HERE? RESULTS ARE IN ALIGN FOLDER BUT ERRORS 11 AND 12 WOULD BE DECIEVING
    #SINCE THE MODULE WOULD AUTOFILL AS ALIGN WHILE THE TRUE MODULE IS RECALIBRATION
    parser.add_argument("-r", "--report", help="report error code")
    parser.add_argument("-u", "--rna", help="rna error code")
    parser.add_argument("-s", "--somatic", help="somatic error code")
    parser.add_argument("-t", "--tcellextrect", help="tcellextrect error code")
    parser.add_argument("-x", "--xhla", help="xhla error code")
    args = parser.parse_args()
    argument_dict = vars(args)
    config_yaml_path = argument_dict.pop("yaml") # config_yaml_path is not a module and should be stored separately
    codes_dict = {key: value for (key, value) in argument_dict.items() if value is not None}
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


    file_dict = create_dict(run_name,TO,tumor,normal)
    create_yaml(run_name, file_dict, codes_dict)

    #write files and track which modules had missing files
    missing=[]
    for module in file_dict:
        for file in file_dict[module]:
            file_writer(file)
            if module not in missing:
                missing.append(module)


    # output missing modules and command
    modules_no_error_code=[key for key in argument_dict if argument_dict[key] == None]
    need_error_code=[m for m in modules_no_error_code if m in missing]
    if need_error_code != []:

        print("The following modules had files missing but no error codes were assigned:")
        print(need_error_code)
        print("Enter the following command to add error codes to all missing files or enter them manually in analysis/error.yaml:")
        print(command_writer(config_yaml_path, codes_dict, need_error_code))

def command_writer(yaml_path, codes_dict, need_error_code):
        str = "./automate_errors.py " + yaml_path
        for module in codes_dict:
            str = str + " --%s %s" % (module, codes_dict[module])
        for module in need_error_code:
            str = str + " --%s <code>" % (module)
        return str


if __name__=='__main__':
    main()
