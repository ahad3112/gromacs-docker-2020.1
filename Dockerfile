###############################################################################################
#
# Gromacs: 2020.1
# OPENMPI-3.0.0
# FFTW-3.3.7 (single precision)
#
###############################################################################################


#############################################################
# openmpi-3.0.0 and fftw-3.3.7 (single precision)
#############################################################
# Base image
FROM ubuntu:latest

# Labelling
LABEL "Muhammed Ahad"="maaahad@gmail.com;ahad3112@yahoo.com"
LABEL version="1.0"

# OpenMPI
ARG OPENMPI_VERSION_MAJOR=3
ARG OPENMPI_VERSION_MINOR=0
ARG OPENMPI_VERSION_MICRO=0
ARG OPENMPI_VERSION=${OPENMPI_VERSION_MAJOR}.${OPENMPI_VERSION_MINOR}.${OPENMPI_VERSION_MICRO}
ARG OPENMPI_MD5=f336c3de793558cb4ac5f93f95670c7c

# FFTW
ARG FFTW_VERSION=3.3.7
ARG FFTW_MD5=0d5915d7d39b3253c1cc05030d79ac47

# GROMACS
ARG GROMACS_VERSION=2020.1
ARG GROMACS_MD5=1c1b5c0f904d4eac7e3515bc01ce3781

# Gromacs Installation option
ARG ARCHITECTURES="SSE2 AVX_256 AVX2_256 AVX_512"
ARG MDRUN_ONLY="OFF OFF OFF OFF"
ARG RDTSCP="ON ON ON ON"
ARG MPI="OFF OFF OFF OFF"
ARG GPU="OFF OFF OFF OFF"
ARG DOUBLE="OFF OFF OFF OFF"

# Number of jobs to be used durin gcompilation
ARG JOBS=2

# install required package
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    cmake \
    make \
    python \
    openssh-client \
    wget \
    g++ \
    gcc

# creating installation directories for openmpi, fftw
# creating required directories
RUN mkdir -p /gromacs-src /gromacs /gromacs/bin \
    /openmpi-src /.openmpi-${OPENMPI_VERSION} \
    /fftw-src /.fftw-${FFTW_VERSION}


#############################################################
# FFTW Installation from source code
#############################################################
WORKDIR /fftw-src

run wget -O fftw.tar.gz http://www.fftw.org/fftw-${FFTW_VERSION}.tar.gz \
    && echo "${FFTW_MD5} fftw.tar.gz" > fftw.tar.gz.md5 \
    && md5sum -c fftw.tar.gz.md5 \
    && gunzip fftw.tar.gz \
    && tar -xvf fftw.tar \
    && cd fftw-${FFTW_VERSION} \
    && ./configure --prefix=/.fftw-${FFTW_VERSION} --disable-double --enable-float --enable-sse2 --enable-avx --enable-avx2 --enable-avx512 --enable-shared --disable-static \
    && make -j ${JOBS} \
    && make install


#############################################################
# OpenMPI Installation from source code
#############################################################
WORKDIR /openmpi-src

RUN wget --no-check-certificate -O openmpi.tar.gz https://download.open-mpi.org/release/open-mpi/v${OPENMPI_VERSION_MAJOR}.${OPENMPI_VERSION_MINOR}/openmpi-${OPENMPI_VERSION}.tar.gz \
    && echo "${OPENMPI_MD5} openmpi.tar.gz" > openmpi.tar.gz.md5 \
    && md5sum -c openmpi.tar.gz.md5 \
    && gunzip openmpi.tar.gz \
    && tar -xvf openmpi.tar \
    && cd openmpi-${OPENMPI_VERSION} \
    && ./configure --prefix=/.openmpi-${OPENMPI_VERSION} \
    && make -j ${JOBS} \
    && make install


#############################################################
# Setting installation path for fftw and openmpi
#############################################################
ENV PATH=/.openmpi-${OPENMPI_VERSION}/bin:/.fftw-${FFTW_VERSION}/bin:$PATH
ENV LD_LIBRARY_PATH=/.openmpi-${OPENMPI_VERSION}/lib:/.fftw-${FFTW_VERSION}/lib:$LD_LIBRARY_PATH


#############################################################
# Gromacs:2020.1 (single precision) Installation
#############################################################

# Setting cmake environment variables for fftw and openmpi for binaries, libraries and include file
ENV CMAKE_PREFIX_PATH=/.openmpi-${OPENMPI_VERSION}:/.fftw-${FFTW_VERSION}

WORKDIR /gromacs-src

# Download
RUN wget -O gromacs.tar.gz http://ftp.gromacs.org/pub/gromacs/gromacs-${GROMACS_VERSION}.tar.gz \
    && echo "${GROMACS_MD5} gromacs.tar.gz" > gromacs.tar.gz.hd5 \
    && md5sum -c gromacs.tar.gz.hd5 \
    && gunzip gromacs.tar.gz \
    && tar -xvf gromacs.tar \
    && mv gromacs-${GROMACS_VERSION}/* .

# Install
COPY build/gromacs_build.py /gromacs-src/build/gromacs_build.py
COPY config.py /gromacs-src/build/config.py
RUN chmod +x /gromacs-src/build/gromacs_build.py

# build.py takes all available cpu instruction set, MDRUN_ONLY,RDTSCP, MPI, GPU and DOUBLE options
RUN /gromacs-src/build/gromacs_build.py -a $ARCHITECTURES -md $MDRUN_ONLY -r $RDTSCP -m $MPI -g $GPU -d $DOUBLE


# setting wrapper as binay and their path along with gmx_chooser.py path
COPY gmx_chooser.py /gromacs/bin/gmx_chooser.py
RUN chmod +x /gromacs/bin/*
COPY config.py /gromacs/bin/config.py

ENV PATH=/gromacs/bin:$PATH


#############################################################
# Cleaning Image unnecessary folders and packages
#############################################################
# Deleting Source files
WORKDIR /
RUN rm -r /gromacs-src /fftw-src /openmpi-src

# Deleting some unnecessary packages
RUN apt-get update \
    && apt-get remove --auto-remove -y \
    wget \
    make \
    cmake

