# ATLAS Failed Job Checker

## Getting credentials
You will need to email Lincoln Bryant (lincolnb@uchicago.edu) or Ilija Vukotic
(ivukotic@uchicago.edu) for read-only credentials to access elastic search at
UChicago.

## Installation / Setup
This software requires either `python36-elasticsearch` and `python36-tabulate` packages installed 
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
