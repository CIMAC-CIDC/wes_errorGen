#!/usr/bin/env python
'''Jacob Geisberg Jan,2022
This script generates all of the missing files required for ingestion
of errored runs based on user input of which modules have failed and their
error codes. Please note that this will overwrite existing files related to
those modules if they exist and are needed for ingestion.'''
import requests
import json
import os
#import sys
import argparse
import yaml
import ruamel.yaml

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
        for f in file[wildcard]:
            path = f['file_path_template']
            module = path.split("/")[1] #second directory in path is always module name
            file_TO = f['tumor_only_assay']
            optional = f['optional']
            #ensures that no normal files are included for TO samples
            exclude = TO and (not file_TO)
            if (not optional) and (module in modules) and (not exclude):
                path = path.replace('{'+ wildcard +'}', wildcards[wildcard])
                if module in dict:
                    dict[module].append(path)
                else:
                    dict[module] = [path]
    return dict

def file_writer(path, text=''):
    '''Writes text to a given path. Will create directories as needed.
    '''
    #overwrite existing file
    if os.path.isfile(path):
        # MAYBE WARN USERS ABOUT OVERWRITE AND ASK FOR AUTHORIZATION
        with open(path, "w") as out_file:
            print("overwriting", path)
            out_file.write(text)

    # check and create needed file structure step by step
    else:
        split = path.split('/')
        directories, name = split[:-1], split[-1]
        existing_path = ""
        for d in directories:
            existing_path = existing_path + d + "/"
            if os.path.isdir(existing_path) == False:
                os.mkdir(existing_path)
        with open(path, "w") as out_file:
            out_file.write(text)
            print("wrote:",  path)


def create_yaml(file_dict, code_nums):
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
    # url = 'https://www.dropbox.com/s/vhfxnn6v3ta6klzFailure_Codes.xlsx?dl=0'
    # file = requests.get(url)
    # print(file.text)

    # Itterates through the file dictionary to write yaml line by line
    text = "---\n\nerrors:\n"
    for module in file_dict:
        code_num = code_nums[module]

        # checks that user error numbers are valid
        if code_num not in code_strings:
            print('please make sure all error codes are valid')
            sys.exit(-1)

        # 11 requires a software field that should be provided once
        if code_num == "11":
            software = raw_input("please enter errored software for %s: " % (module))

        # generates appropriate entry for each file based on error code
        for file in file_dict[module]:
            message = '  %s: "ERROR%s: %s"\n' % (file, code_num,code_strings[code_num])
            # 11 and 12 are special cases that require string replacement
            if code_nums[module] == "11":
                message = message.replace("XXX", software)
            elif code_nums[module] == "12":
                message = message.replace("XXX", module)
            text = text + message
    return text


#main function
def main():

    parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter, # keep newlines
    description="Simply add the corresponding error code for each failed module \nex. -n 30 -c 21 \nsee dropbox for error codes" )

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
    parser.add_argument("-t", "--rna", help="rna error code")
    parser.add_argument("-s", "--somatic", help="somatic error code")
    parser.add_argument("-x", "--xhla", help="xhla error code")
    args = parser.parse_args()
    codes_dict = vars(args)
    codes_dict = {key: value for (key, value) in codes_dict.items() if value is not None}
    modules = [x for x in codes_dict]

    #search for config yaml in current directory, error if there is not 1
    yamls = [file for file in os.listdir(".") if file.endswith(".yaml")]
    if len(yamls) != 1:
        print("\nERROR please make sure you are in the wes directory and that exactly one .yaml file is present.")
        sys.exit(-1)

    # open yaml file
    with open(yamls[0], "r") as yaml_file:
        try:
            yaml_dict = yaml.safe_load(yaml_file)

        except yaml.YAMLError as error:
            print(error)

    #interpret yaml to get run, tumor, and normal ids
    samples = yaml_dict["metasheet"]
    run_name = samples.keys()[0]
    tumor = samples[run_name]["tumor"]
    if "normal" in samples[run_name].keys():
        normal = samples[run_name]['normal']
        TO = False
    else:
        normal = None
        TO = True


    file_dict = create_dict(run_name, modules,TO,tumor,normal)
    yaml_text = create_yaml(file_dict, codes_dict)
    path = "analysis/%s_error.yaml" % (run_name)
    file_writer(path,yaml_text)
    for module in file_dict:
        for file in file_dict[module]:
            file_writer(file)





if __name__=='__main__':
    main()
