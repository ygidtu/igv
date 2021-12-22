# igv

Simple online igv browser based on [igv.js](https://github.com/igvteam/igv.js).

## Why?
Due to the limitation of our servers, it's quite difficult to setup  jbrowser.

## requirements
### node.js
- axios: "^0.24.0",
- core-js: "^3.6.5",
- element-ui: "^2.14.1",
- igv: "^2.10.5",
- vue: "^2.6.11",
- vue-axios: "^3.4.0",
- vue-router: "^3.5.3"

### Python
- click = "*"
- jinja2 = "*"
- filetype = "*"
- pysam = "*"

## Installation

```bash
git clone https://github.com/ygidtu/igv.git
cd igv

# prepare the web frontend interface
npm install -g @vue/cli
# OR
yarn global add @vue/cli

yarn build

# setup python env
## pip
pip install -r requirements.txt

## pipenv
pipenv install
pipenv shell
```


## Usage

```bash
➜ python main.py --help
Usage: main.py [OPTIONS]

Options:
  -h, --host TEXT     The host address.   [default: 127.0.0.1]
  -p, --port INTEGER  The port listen to.   [default: 5000]
  -k, --key PATH      The path to ssl key file.
  -c, --cert PATH     The path to ssl cert file.
  -g, --gtf PATH      The path to reference gtf file.   [required]
  -f, --fasta PATH    The path to fasta file.   [required]
  -b, --bam PATH      The path to directory contains bam files.   [required]
  --version           Show the version and exit.
  --help              Show this message and exit.
```

> The -b/--bam have two conditions
> 1. all the bam or bedgraph files located in same directory. bedgraph file name **must end with** .bdg.gz or .bedgraph.gz (case ignore)。
> 2. there are bams/bedgraphs from different groups, then seperate those files by different directory：    
    - group1/(bams/bedgraphgs)     
    - group2/(bams/bedgraphgs)   
