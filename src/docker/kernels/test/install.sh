#!/bin/bash
conda create -y -n test python=3.11
/opt/conda/envs/test/bin/pip install ipykernel
/opt/conda/envs/test/bin/pip install --no-cache-dir \
    -r /tmp/common-packages.txt \
    -r /tmp/test/requirement.txt
/opt/conda/envs/test/bin/python -m ipykernel install --user --name=test --display-name "test"