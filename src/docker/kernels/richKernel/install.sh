#!/bin/bash
conda create -y -n richKernel python=3.11
/opt/conda/envs/richKernel/bin/pip install ipykernel
/opt/conda/envs/richKernel/bin/pip install --no-cache-dir \
    -r /tmp/common-packages.txt \
    -r /tmp/richKernel/requirement.txt
/opt/conda/envs/richKernel/bin/python -m ipykernel install --user --name=richKernel --display-name "richKernel"