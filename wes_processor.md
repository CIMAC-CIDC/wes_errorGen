#Wes Processor Script for Automated Ingestion Prep

##Why use wes processor?
Use wes processor prior to ingestion of errored samples after you have completed as many modules as possible. By using wes processor to review and document all downstream files of an error, you can be sure that the sample will be ready for ingestion.

##How to start wes processor
The first step is to run wes_processor.py with the -h argument of get a sense of the options. Currently wes processor only works when run from the wes_errorgen directory.
```
./wes_processor.py -h               
usage: wes_processor.py [-h] -j JOB [--folder FOLDER] [-d DAG] [-m METASHEET] [-t TUMOR_ONLY]

Finds all affected files from a given error, generates blank files that are needed for ingestion, and allows easy construction of error.yaml

options:
  -h, --help            show this help message and exit
  -j JOB, --job JOB     job id number that errored out
  --folder FOLDER       location of WES results. default: /mnt/ssd/wes/
  -d DAG, --dag DAG     file containing a complete dag of the run. can be generated with: snakemake -s
                        cidc_wes/wes.snakefile --forceall -n --dag > sample_dag.dot
  -m METASHEET, --metasheet METASHEET
                        name of the metasheet used. default: metasheet.csv
  -t TUMOR_ONLY, --tumor_only TUMOR_ONLY
                        whether the sample was run with a matched normal
```

Currently, the only _required_ argument is the job number of the rule that errored out. This can be found in the nohup.out file. The job id tells wes processor the starting point in the pipeline from which you would like to examine and document files. If you would like to start earlier or later than the actual error in the pipeline, that is ok if you know what you are doing.

The ```--folder``` argument denotes the path to folder containing your wes results. The default value is '/mnt/ssd/wes/'. Set this parameter if you have results in a different location or if you wish to experiment with wes processor without modifying your results folder. Using an absolute path is recommended, and a trailing "/" is optional.

The ```--dag``` argument is for supplying the path of your own snakemake dag to wes processor. If you are ingesting the sample to the CIDC portal, You should absolutely not set this argument unless you are sure that your alternative workflow covers all of the files that will be ingested.

The ```--metasheet``` argument will change the name of the metasheet used to determine sample names for the run. The metasheet is assumed to be in the ```--folder``` directory, so the metasheet argument should not be changed unless the filename differs from "metasheet.csv"

The ```--tumor_only``` argument should be set to True if you ran a tumor_only sample.

#Working with wes processor
Once you have started wes processor, It will begin by creating the complete list of ingested files that could be affected by the job you entered. This includes the files output from the job itself as well as any that are downstream of those. If the list does not look correct, you can safely exit out of the program and make changes as need.

Next, you will see a prompt like this:

```
CURRENT FILE: ./analysis/cnvkit/cww/cww_cnvkit_gainLoss.bed
FILE STATUS: uncertain
FILE PREVIEW:
chrom	start	end	total_cn	call
chr1	10500	29150192	1	LOSS
chr1	29154717	31618692	3	GAIN
chr1	31619192	31815333	1	LOSS
chr1	31815833	33181228	4	GAIN
END FILE PREVIEW
Enter a valid error code. Press 'e' to view error codes, f to view file_path, and 'ENTER' to add no error:
```
The top line is the path to the file that we are examining. The second line is the file status and can be "missing", "empty", or "uncertain". If the file is missing, wes processor will create a blank file. If the file already exists but is empty, nothing extra occurs. If the file exists and is not empty, the file status is marked as uncertain and a file preview of the first five lines is shown. The preview is to help ensure that files with N/A or other problematic values are caught and can be documented. Below the information about the file, we request an error code from the user for the file. If you are not familiar with the error codes, type "e" to get a list. In some cases, wes processor will ask for additional input from the user related to the specific error type. In most cases, the file will not require an error code at all, and we can press enter.

After the error prompt, we can add a comment to the file if needed. The only distinction is that we can use "p" to repeat the previous comment. In addition, you will be prompted to confirm each comment.

```
Enter a comment, press 'p' to repeat previous comment, or press 'Enter' to skip: This is a comment
You are about to add 'This is a comment' as a comment to analysis/cnvkit/cww/cww_cnvkit_gainLoss.bed. Is this ok (y/n): y
```
