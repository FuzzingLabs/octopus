# Docker Image with Octopus

# Pull base image
FROM ubuntu:16.04
LABEL maintainer="rui@computer.org"

# Install Python and build tools
RUN \
  apt-get update && \
  apt-get install -y build-essential software-properties-common libssl-dev wget && \
  apt-get install -y python python-dev python-pip git psmisc lsof graphviz python3-pip xdg-utils

#Install Python3.6
RUN \
  add-apt-repository ppa:jonathonf/python-3.6 -y && \
  apt-get update && \
  apt-get install python3.6 -y && \
  update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.5 1 && \
  update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 2 

# Install Octopus from GitHub
RUN \
  git clone https://github.com/quoscient/octopus

# Install dependencies
RUN \
  pip3 install --upgrade pip

RUN \
  pip3 install -r octopus/requirements.txt

# Install Octopus library/CLI and its dependencies
RUN \
  cd octopus && \ 
  python3 setup.py install

# Grant exec rights
RUN \ 
  cd /octopus/octopus/tests && \
  chmod +x *.sh 

# Run ETH tests
RUN \ 
  cd /octopus/octopus/tests && \
  ./eth_run_tests.sh

RUN \
  echo "##############################################################################" && \
  echo "Run 'docker run -it octopus' and check the octopus folder out." && \
  echo "example: python3 octopus_eth_evm.py -s -f examples/ETH/evm_bytecode/61EDCDf5bb737ADffE5043706e7C5bb1f1a56eEA.bytecode" && \
  echo "##############################################################################" 