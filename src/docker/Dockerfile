FROM jupyter/base-notebook

USER root
RUN apt-get update && apt-get install -y build-essential

USER $NB_UID
COPY base/common-packages.txt /tmp/

COPY kernels/richKernel /tmp/richKernel
RUN bash /tmp/richKernel/install.sh

COPY kernels/test /tmp/test
RUN bash /tmp/test/install.sh

USER root
RUN rm -rf /tmp/*
USER $NB_UID