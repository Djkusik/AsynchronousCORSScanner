# Asynchronous CORSScanner
> CORS misconfiguration scanner made with asyncio and aiohttp for the fastest execution

## Installation

Raw install:
```sh
git clone https://github.com/Djkusik/AsynchronousCORSScanner.git
cd AsynchronousCORSScanner
pip install -r requirements.txt
```

Using docker:
```sh
docker build -t cors_scanner .
```

### Usage example

```sh
python cors_scanner.py -d example.com -v 5 -f output.log
python cors_scanner.py -l top_100.txt

# Or with docker
docker run -v ~/:/home/cors_scanner/report --user $(id -u):cors_scanner cors_scanner -d example.com -r
```

### Flags

```
usage: cors_scanner.py [-h] [-l LIST] [-d DOMAIN] [-v {1,2,3,4,5}] [-f FILE]
                       [-c {0,1,2}] [-r] [-rp REPORT_PATH]

optional arguments:
  -h, --help                                    show this help message and exit
  -l LIST, --list LIST                          path to file with domain list
  -d DOMAIN, --domain DOMAIN                    domain to test
  -v {1,2,3,4,5}, --verbosity {1,2,3,4,5}       logging level
  -f FILE, --file FILE                          path to log file
  -c {0,1,2}, --char {0,1,2}                    bigger number will result in wider 
                                                tests which uses special characters
  -r, --report                                  create report
  -rp REPORT_PATH, --report-path REPORT_PATH    path where to create a report
```

## Meta

Paweł Kusiński

Distributed under the BSD 2-Clause License. See ``LICENSE`` for more information.