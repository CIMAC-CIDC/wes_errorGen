## wes_errorgen script for automating error file generation in the WES pipilene

### Why use wes_errorgen?
In order for the CIMAC-CIDC portal to ingest a sample, the sample needs to have a specific set of files. The current set of files required for WES samples can be found [here](https://github.com/CIMAC-CIDC/cidc-ngs-pipeline-api/blob/master/cidc_ngs_pipeline_api/wes/wes_output_API.json). Unfortunately, when modules are skipped, some of the files are not created and the sample cannot be ingested. This is where wes_errorgen comes in! Instead of manually determining and creating missing files, you can use wes_errorgen to do it for you. It can even create the error.yaml file for you, saving lots of time.  

### How to run wes_errorgen

Before you start, make sure that you are in the wes directory of the instance for which you intend to generate error files. Next, ensure that "automate_errors.py" and the setup yaml file, often named "sample_name.yaml" or "sample_name_processed.yaml", are also located in the wes directory. While this is not strictly necessary, it will make running the script easier. Finally, consult the [error code document](https://www.dropbox.com/s/vhfxnn6v3ta6klz/Failure_Codes.xlsx?dl=0) and make note of error codes for each module that failed.

With the setup complete, a good first step is to run automate_errors.py with the help argument to get a better idea of how the script works.

```bash
python automate_errors.py -h
usage: automate_errors.py [-h] [-a ALIGN] [-c CLONALITY] [-d COPYNUMBER]
                          [-e COVERAGE] [-g GERMLINE] [-m METRICS]
                          [-q MISSENSOR2] [-n NEOANTIGEN] [-o OPTITYPE]
                          [-p PURITY] [-r REPORT] [-t RNA] [-s SOMATIC]
                          [-x XHLA]
                          yaml

Simply add name of the setup yaml and the corresponding error code for each failed module
ex. -n 30 -c 21
see dropbox for error codes

positional arguments:
  yaml                  (REQUIRED) name of the yaml used to generate the
                        instance

optional arguments:
  -h, --help            show this help message and exit
  -a ALIGN, --align ALIGN
                        align module error code
  -c CLONALITY, --clonality CLONALITY
                        clonality error code
  -d COPYNUMBER, --copynumber COPYNUMBER
                        copynumber error code
  -e COVERAGE, --coverage COVERAGE
                        coverage error code
  -g GERMLINE, --germline GERMLINE
                        germline error code
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
  -t RNA, --rna RNA     rna error code
  -s SOMATIC, --somatic SOMATIC
                        somatic error code
  -x XHLA, --xhla XHLA  xhla error code
```
While the help message is pretty robust, if you are already familiar with the program or want a shorter output, running the script without the help argument will provide a more concise output.
```bash
python automate_errors.py   
usage: automate_errors.py [-h] [-a ALIGN] [-c CLONALITY] [-d COPYNUMBER]
                          [-e COVERAGE] [-g GERMLINE] [-m METRICS]
                          [-q MISSENSOR2] [-n NEOANTIGEN] [-o OPTITYPE]
                          [-p PURITY] [-r REPORT] [-t RNA] [-s SOMATIC]
                          [-x XHLA]
                          yaml
automate_errors.py: error: too few arguments
```

As you can see, the script takes one required argument called "yaml" and a bunch of optional arguments, one for each module. The yaml argument is just the path to the sample setup yaml file, and since we made sure that it was in our current directory, this is just the name of the file. The optional module arguments just take the error code number for the type of failure that the module experienced. Running a simple example in which clonality ran out of disk space (error code 21) and neoantigen stalled out (error code 30) would look like this.

```bash
python automate_errors.py sample.yaml -c 21 -n 30
('wrote:', 'analysis/C3RX3ZSEU.01_error.yaml')
('wrote:', u'analysis/neoantigen/C3RX3ZSEU.01/combined/C3RX3ZSEU.01.filtered.tsv')
('wrote:', u'analysis/clonality/C3RX3ZSEU.01/C3RX3ZSEU.01_pyclone.tsv')
('wrote:', u'analysis/clonality/C3RX3ZSEU.01/C3RX3ZSEU.01_table.tsv')
```
That's it. We've successfully created the error.yaml file and all of the other missing files for the clonality and neoantigen modules. However, running the same command will give a slightly different output.
```
python automate_errors.py sample.yaml -c 21 -n 30
('overwriting', 'analysis/C3RX3ZSEU.01_error.yaml')
('overwriting', u'analysis/neoantigen/C3RX3ZSEU.01/combined/C3RX3ZSEU.01.filtered.tsv')
('overwriting', u'analysis/clonality/C3RX3ZSEU.01/C3RX3ZSEU.01_pyclone.tsv')
('overwriting', u'analysis/clonality/C3RX3ZSEU.01/C3RX3ZSEU.01_table.tsv')
```
As you can see, the script will overwrite its target files if they already exist. In case you would like to preserve some partially complete modules for ingestion, do not use errorgen.
