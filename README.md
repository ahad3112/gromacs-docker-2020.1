# GROMACS 2020.1

[![Docker image releases](https://img.shields.io/github/release/bioexcel/gromacs-docker.svg)](https://github.com/bioexcel/gromacs-docker/releases)
[![bioexcel/gromacs](https://img.shields.io/badge/docker-gromacs%2Fgromacs-1488C6.svg?logo=docker)](https://hub.docker.com/r/gromacs/gromacs/ "gromacs/gromacs")

## Building Image

Building image is initiated by `docker_build.py` script. One can choose to install multiple version GROMACS based on the following options:

* SIMD instruction set, choose from [sse2, avx_256, avx2_256, avx_512]
* MPI enabled/disabled
* rdtscp enabled/disabled
* mdrun_only enabled/disabled
* double precision on/off (Not functioning at this moment. Single precision will be used for now)
* GPU enabled/disabld (Not functioning at this moment. Will be disabled for now)

Avaibale option of `docker_build.py` can be viewed as follows:

    cd build
    ./docker_build.py -h
    usage: docker_build.py [-h] -n NAME -a {sse2,avx_256,avx2_256,avx_512}
                       [{sse2,avx_256,avx2_256,avx_512} ...] -md {on,off}
                       [{on,off} ...] [-r {on,off} [{on,off} ...]]
                       [-m {on,off} [{on,off} ...]]
                       [-g {on,off} [{on,off} ...]]
                       [-d {on,off} [{on,off} ...]] [-y]

## Running Image
The Available GROMACS wrapper binaries will be the followings based on `mpi` enabled or disabled and `mdrun_only` enabled or disabled:

* `gmx`
* `gmx_mpi`
* `mdrun`
* `mdrun_mpi`

Wrapper binaries `mdrun` and `mdrun_mpi` represent `mdrun_only` installation of GROMACS.
To use other GROMACS tools such as `pdb2gmx`, `grompp`, `editconf` etc. full installation
of GROMACS are required. Full installation of GROMACS are wrapped within `gmx` and `gmx_mpi`.

```Without Singularity : ```

Bind the directory that you want Docker to get access to. Below is an example of running `mdrun` module using `gmx` wrapper:

    mkdir $HOME/data
    docker run -v $HOME/data:/data -w /data -it <image_name> gmx mdrun -s <.tpr file> -deffnm <ouput_file_name>

```With Singularity : ```


## Contribute

