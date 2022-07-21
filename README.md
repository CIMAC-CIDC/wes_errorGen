## wes_errorgen script for automating error file generation in the WES pipilene

### Why use wes_errorgen?
In order for the CIMAC-CIDC portal to ingest a sample, the sample needs to have a specific set of files. The current set of files required for WES samples can be found [here](https://github.com/CIMAC-CIDC/cidc-ngs-pipeline-api/blob/master/cidc_ngs_pipeline_api/wes/wes_output_API.json). Unfortunately, when modules are skipped, some of the files are not created and the sample cannot be ingested. This is where wes_errorgen comes in! Instead of manually determining and creating missing files, you can use wes_errorgen to do it for you. It can even create the error.yaml file for you, saving lots of time.  

### How to run wes_errorgen
Before you start, make sure that you are in the wes directory of the instance for which you intend to generate error files. The first step is to clone the repository containing the automate_errors script. This can be done by ssh or by HTTPS.
```bash
#SSH
git clone git@bitbucket.org:plumbers/wes_errorgen.git

#HTTPS
git clone https://jberg1999-admin@bitbucket.org/plumbers/wes_errorgen.git
```

Next, ensure that "automate_errors.py" and the setup yaml file, often named "SAMPLENAME.yaml" or "SAMPLENAME_processed.yaml", are also located in the wes directory. While this is not strictly necessary, it will make running the script easier.

With the setup complete, a good first step is to run automate_errors.py with the help argument to get a better idea of how the script works.

```bash
./automate_errors.py -h
usage: automate_errors.py [-h] [-a ALIGN] [-c CLONALITY] [-d CNVKIT]
                          [-e COPYNUMBER] [-f COVERAGE] [-g GERMLINE]
                          [-i HLAHD] [-m METRICS] [-q MISSENSOR2]
                          [-n NEOANTIGEN] [-o OPTITYPE] [-p PURITY]
                          [-r REPORT] [-u RNA] [-s SOMATIC] [-t TCELLEXTRECT]
                          [-x XHLA]
                          yaml

Simply add name of the wes_automator yaml and the corresponding error code for each failed module
ex. ./automate_errors.py -n 30 -c 21

positional arguments:
  yaml                  (REQUIRED) name of the yaml used to generate the
                        instance

options:
  -h, --help            show this help message and exit
  -a ALIGN, --align ALIGN
                        align module error code
  -c CLONALITY, --clonality CLONALITY
                        clonality error code
  -d CNVKIT, --cnvkit CNVKIT
                        cnvkit error code
  -e COPYNUMBER, --copynumber COPYNUMBER
                        copynumber error code
  -f COVERAGE, --coverage COVERAGE
                        coverage error code
  -g GERMLINE, --germline GERMLINE
                        germline error code
  -i HLAHD, --hlahd HLAHD
                        hlahd error code
  -m METRICS, --metrics METRICS
                        metrics error code
  -q MISSENSOR2, --missensor2 MISSENSOR2
                        missensor2 error code
  -n NEOANTIGEN, --neoantigen NEOANTIGEN
                        neoantigen error code
  -o OPTITYPE, --optitype OPTITYPE
                        optitype error code
  -p PURITY, --purity PURITY
                        purity error code
  -r REPORT, --report REPORT
                        report error code
  -u RNA, --rna RNA     rna error code
  -s SOMATIC, --somatic SOMATIC
                        somatic error code
  -t TCELLEXTRECT, --tcellextrect TCELLEXTRECT
                        tcellextrect error code
  -x XHLA, --xhla XHLA  xhla error code

error codes:
00: Unknown error
01: Data file corrupt or unreadable
02: PE reads incorrectly paired
03: Poor read quality
04: Too few reads
05: Duplicate normal sample -- not used for analysis
11: External software bug/issue {software: XXX}
12: WES pipeline software bug/issue {module: XXX}
21: Out of disk space error
22: Out of memory error
23: Unexpected interruption of service
30: Did not finish computation after 6 hours
```
As you can see, the script takes one required argument called "yaml" and a bunch of optional arguments, one for each module. The yaml argument is just the path to the sample wes_automator yaml file, and since we made sure that we are in the correct directory, this is just the name of the file. The optional module arguments take the error code number for the type of failure that the module experienced. The help message also displays the possible error codes, which can also be found [here](https://www.dropbox.com/s/vhfxnn6v3ta6klz/Failure_Codes.xlsx?dl=0). In general, it is a good idea to check the link to make sure that the script is up to date.

While the help message is pretty robust, if you are already familiar with the program or want a shorter output, running the script without the help argument will provide a more concise output.
```bash
./automate_errors.py   
usage: automate_errors.py [-h] [-a ALIGN] [-c CLONALITY] [-d CNVKIT]
                          [-e COPYNUMBER] [-f COVERAGE] [-g GERMLINE]
                          [-i HLAHD] [-m METRICS] [-q MISSENSOR2]
                          [-n NEOANTIGEN] [-o OPTITYPE] [-p PURITY]
                          [-r REPORT] [-u RNA] [-s SOMATIC]
                          [-t TCELLEXTRECT] [-x XHLA]
                          yaml
automate_errors.py: error: the following arguments are required: yaml
```

Running a simple example in which align stalled out (error code 30) and neoantigen faced and unknown error (error code 00) would look like this, depending on which specific files are missing.

```bash
./automate_errors.py sample.yaml -a 30 -n 00
successfully wrote yaml to: analysis/C3RX3ZSEU.01_error.yaml
wrote: analysis/neoantigen/C3RX3ZSEU.01/combined/C3RX3ZSEU.01.filtered.tsv
wrote: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01.sorted.dedup.bam
wrote: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01.sorted.dedup.bam.bai
wrote: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01_recalibrated.bam
wrote: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01_recalibrated.bam.bai
wrote: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01.sorted.dedup.bam
wrote: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01.sorted.dedup.bam.bai
wrote: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01_recalibrated.bam
wrote: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01_recalibrated.bam.bai
```
The script will display each file that that it has successfully written. However running the command again will produce a different result as the script will not overwrite existing files, other than the error.yaml.

```bash
./automate_errors.py sample.yaml -a 30 -n 00
successfully wrote yaml to: analysis/C3RX3ZSEU.01_error.yaml
existing blank file: analysis/neoantigen/C3RX3ZSEU.01/combined/C3RX3ZSEU.01.filtered.tsv
existing blank file: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01.sorted.dedup.bam
existing blank file: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01.sorted.dedup.bam.bai
existing blank file: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01_recalibrated.bam
existing blank file: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01_recalibrated.bam.bai
existing blank file: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01.sorted.dedup.bam
existing blank file: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01.sorted.dedup.bam.bai
existing blank file: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01_recalibrated.bam
existing blank file: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01_recalibrated.bam.bai
```

The script can also handle a mix of existing and new files. Lets add an external software issue to the report module.
```bash
python automate_errors.py sample.yaml -a 30 -n 00 -r 11
Please enter errored software for report:
```
Unlike some of the other error codes, automate errors needs help from the user to write the error.yaml file for external software errors. This is because it has no way to infer which software broke and this information is required to write the entry in the yaml file. After typing "foo" as the broken software, the script is able to complete. In this case it wrote all of the required report files while preserving the existing align and neoantigen files.

```bash
./automate_errors.py sample.yaml -a 30 -n 00 -r 11
Please enter errored software for report: foo
successfully wrote yaml to: analysis/C3RX3ZSEU.01_error.yaml
existing blank file: analysis/neoantigen/C3RX3ZSEU.01/combined/C3RX3ZSEU.01.filtered.tsv
wrote: analysis/report/somatic_variants/05_tumor_germline_overlap.tsv
wrote: analysis/report/WES_Meta/02_WES_Run_Version.tsv
wrote: analysis/report/config.yaml
wrote: analysis/report/metasheet.csv
wrote: analysis/report/json/C3RX3ZSEU.01.wes.json
existing blank file: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01.sorted.dedup.bam
existing blank file: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01.sorted.dedup.bam.bai
existing blank file: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01_recalibrated.bam
existing blank file: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01_recalibrated.bam.bai
existing blank file: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01.sorted.dedup.bam
existing blank file: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01.sorted.dedup.bam.bai
existing blank file: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01_recalibrated.bam
existing blank file: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01_recalibrated.bam.bai

```
Another useful feature is that the script will also catch files that the user may have forgotten and suggest a command that would assign error codes to all of the missing files. Let say we had missing files from align, neoantigen and report, but only entered in code for the first two.

```bash
successfully wrote yaml to: analysis/C3RX3ZSEU.01_error.yaml
existing blank file: analysis/neoantigen/C3RX3ZSEU.01/combined/C3RX3ZSEU.01.filtered.tsv
wrote: analysis/report/somatic_variants/05_tumor_germline_overlap.tsv
wrote: analysis/report/WES_Meta/02_WES_Run_Version.tsv
wrote: analysis/report/config.yaml
wrote: analysis/report/metasheet.csv
wrote: analysis/report/json/C3RX3ZSEU.01.wes.json
existing blank file: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01.sorted.dedup.bam
existing blank file: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01.sorted.dedup.bam.bai
existing blank file: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01_recalibrated.bam
existing blank file: analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01_recalibrated.bam.bai
existing blank file: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01.sorted.dedup.bam
existing blank file: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01.sorted.dedup.bam.bai
existing blank file: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01_recalibrated.bam
existing blank file: analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01_recalibrated.bam.bai
The following modules had files missing but no error codes were assigned:
['report']
Enter the following command to add error codes to all missing files or enter them manually in analysis/error.yaml:
./automate_errors.py sample.yaml --align 30 --neoantigen 00 --report <code>
```

In this case, we now have a complete set of files in the analysis directory, but our error.yaml does not have error codes filled in for the report files since we did not provide any. Running the suggested command with a code filled in for report would ensure that the error.yaml is complete.


With our work finished, we can check in on our error.yaml file to ensure it is correct. As a bonus, automate errors will alphabetize the lines ensuring that each module's error files are adjacent.

```
cat analysis/C3RX3ZSEU.01_error.yaml
errors:
  analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01.sorted.dedup.bam: 'ERROR30: Did not finish computation after 6 hours'
  analysis/align/C3RX3ZS7Q.01/C3RX3ZS7Q.01.sorted.dedup.bam.bai: 'ERROR30: Did not finish computation after 6 hours'
  analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01.sorted.dedup.bam: 'ERROR30: Did not finish computation after 6 hours'
  analysis/align/C3RX3ZSEU.01/C3RX3ZSEU.01.sorted.dedup.bam.bai: 'ERROR30: Did not finish computation after 6 hours'
  analysis/neoantigen/C3RX3ZSEU.01/combined/C3RX3ZSEU.01.filtered.tsv: 'ERROR00: Unknown error'
  analysis/report/WES_Meta/02_WES_Run_Version.tsv: 'ERROR11: External software bug/issue {software: foo}'
  analysis/report/config.yaml: 'ERROR11: External software bug/issue {software: foo}'
  analysis/report/json/C3RX3ZSEU.01.wes.json: 'ERROR11: External software bug/issue {software: foo}'
  analysis/report/metasheet.csv: 'ERROR11: External software bug/issue {software: foo}'
  analysis/report/neoantigens/01_HLA_Results.tsv: 'ERROR11: External software bug/issue {software: foo}'
  analysis/report/somatic_variants/05_tumor_germline_overlap.tsv: 'ERROR11: External software bug/issue {software: foo}'
```
