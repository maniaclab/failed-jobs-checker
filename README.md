# ATLAS Failed Job Checker

## Getting credentials
You will need to email Lincoln Bryant (lincolnb@uchicago.edu) or Ilija Vukotic
(ivukotic@uchicago.edu) for read-only credentials to access elastic search at
UChicago.

## Installation / Setup
This software requires both `python36-elasticsearch` and `python36-tabulate` packages installed, either through system packages or virtual environment.

### CentOS 7 
```
yum install python36-elasticsearch6
yum install python36-tabulate
```

### Virtual Environment
```
python3.6 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

You will need to export the `ES_USER` and `ES_PASS` variables into your
environment that match the credentials you requested above.

```bash
$ ./check2.py --help
usage: FailedJobs [-h] [-s SITE] [-i IDS [IDS ...]] [-l LAST] {site,node}

Query ATLAS Analytics Elasticsearch for failed jobs

positional arguments:
  {site,node}

optional arguments:
  -h, --help            show this help message and exit
  -s SITE, --site SITE  Site, e.g. 'MWT2', 'AGLT2', 'SWT2_CPB', etc
  -i IDS [IDS ...], --ids IDS [IDS ...]
                        space separated list of PanDA job IDs
  -l LAST, --last LAST  Maximum number of hours ago. Only relevant for 'site'
                        mode
```

### Site mode
This mode will look at failures across the entire site for a given number of
hours before the current time.

#### Site mode example
```bash
$ ./check2.py site -s MWT2 -l 1
pandaid                                          batchid                                  modificationhost                                 piloterrorcode
-----------------------------------------------  ---------------------------------------  ---------------------------------------------  ----------------
https://bigpanda.cern.ch/job?pandaid=6069497346  iut2-gk02.mwt2.org#9398499.0#1704436223  slot1_24@iut2-c396.iu.edu                                     0
https://bigpanda.cern.ch/job?pandaid=6069648316  uiuc-gk02.mwt2.org#1418461.0#1704446683  slot1_7@uct2-c654.mwt2.org                                 1305
https://bigpanda.cern.ch/job?pandaid=6069652861  uct2-gk02.mwt2.org#8772333.0#1704447294  slot1_3@cit2-c071.mwt2.org                                 1305
https://bigpanda.cern.ch/job?pandaid=6069287664  iut2-gk02.mwt2.org#9395973.0#1704414228  slot1_11@iut2-c307.iu.edu                                     0
https://bigpanda.cern.ch/job?pandaid=6069640354  iut2-gk02.mwt2.org#9400250.0#1704445812  slot1_30@mwt2-c201.campuscluster.illinois.edu              1305
https://bigpanda.cern.ch/job?pandaid=6069633343  uct2-gk02.mwt2.org#8771860.0#1704445805  slot1_22@mwt2-c141.campuscluster.illinois.edu              1305
https://bigpanda.cern.ch/job?pandaid=6069625491  uiuc-gk02.mwt2.org#1418224.0#1704444378  slot1_27@iut2-c340.iu.edu                                  1305
https://bigpanda.cern.ch/job?pandaid=6069608909  uct2-gk02.mwt2.org#8771359.0#1704441618  slot1_17@uct2-c507.mwt2.org                                1305
https://bigpanda.cern.ch/job?pandaid=6069633964  uct2-gk.mwt2.org#8739758.0#1704434949    slot1_1@uct2-c576.mwt2.org                                 1098
```

### Node mode
This mode will attempt to locate the HTCondor `EXECUTE_DIR` directory and grep
the job's stdout for the Pilot ID for each job running at the site.

Otherwise, PanDA job IDs can be supplied via the `-i` or `--ids` flags. 

#### Supplying IDs Example
```bash
$ ./check2.py node -i 6069633343
pandaid                                          modificationhost                                 piloterrorcode  jobstatus
-----------------------------------------------  ---------------------------------------------  ----------------  -----------
https://bigpanda.cern.ch/job?pandaid=6069633343  slot1_22@mwt2-c141.campuscluster.illinois.edu              1305  failed
```

#### Node Search Example
```bash
(venv) [10:01] uct2-c578.mwt2.org:~/failed-jobs-py $ sudo ./check2.py node
pandaid                                          modificationhost               piloterrorcode  jobstatus
-----------------------------------------------  ---------------------------  ----------------  -----------
https://bigpanda.cern.ch/job?pandaid=6069660793  slot1_16@uct2-c578.mwt2.org              1098  failed
https://bigpanda.cern.ch/job?pandaid=6069661283  slot1_18@uct2-c578.mwt2.org              1305  failed
https://bigpanda.cern.ch/job?pandaid=6069687372  slot1_9@uct2-c578.mwt2.org               1305  failed
https://bigpanda.cern.ch/job?pandaid=6069630217  slot1_6@uct2-c578.mwt2.org                  0  failed
https://bigpanda.cern.ch/job?pandaid=6069115751  slot1_3@uct2-c578.mwt2.org                  0  failed
https://bigpanda.cern.ch/job?pandaid=6069687373  slot1_7@uct2-c578.mwt2.org                  0  failed
https://bigpanda.cern.ch/job?pandaid=6069700489  slot1_9@uct2-c578.mwt2.org                  0  failed
https://bigpanda.cern.ch/job?pandaid=6069659220  slot1_14@uct2-c578.mwt2.org              1098  failed
https://bigpanda.cern.ch/job?pandaid=6069112758  slot1_3@uct2-c578.mwt2.org               1305  failed
https://bigpanda.cern.ch/job?pandaid=6069242358  slot1_11@uct2-c578.mwt2.org              1098  failed
https://bigpanda.cern.ch/job?pandaid=6069661442  slot1_14@uct2-c578.mwt2.org                 0  failed
https://bigpanda.cern.ch/job?pandaid=6069630218  slot1_1@uct2-c578.mwt2.org                  0  failed
https://bigpanda.cern.ch/job?pandaid=6069630219  slot1_11@uct2-c578.mwt2.org                 0  failed
https://bigpanda.cern.ch/job?pandaid=6069115749  slot1_4@uct2-c578.mwt2.org                  0  failed
https://bigpanda.cern.ch/job?pandaid=6069661445  slot1_16@uct2-c578.mwt2.org                 0  failed
https://bigpanda.cern.ch/job?pandaid=6069661490  slot1_18@uct2-c578.mwt2.org                 0  failed
https://bigpanda.cern.ch/job?pandaid=6069242357  slot1_6@uct2-c578.mwt2.org               1098  failed
https://bigpanda.cern.ch/job?pandaid=6069242356  slot1_1@uct2-c578.mwt2.org               1098  failed
https://bigpanda.cern.ch/job?pandaid=6069112757  slot1_4@uct2-c578.mwt2.org               1305  failed
https://bigpanda.cern.ch/job?pandaid=6069660442  slot1_15@uct2-c578.mwt2.org              1098  failed
https://bigpanda.cern.ch/job?pandaid=6069661446  slot1_15@uct2-c578.mwt2.org                 0  failed
```
