#!/usr/bin/env python
import sys
import argparse
import os

import config


GROMACS_INSTALL_PREFIX = '/gromacs'
BINARY = os.path.join(GROMACS_INSTALL_PREFIX, 'bin')
GROMACS_SOURCE_DIR = '/gromacs-src'
GROMACS_BUILD_DIR = 'gromacs-build.{0}'  # relative to GROMACS_SOURCE_DIR

JOBS = 2


# cmake options : WE ARE NOT CONSIDERING GPU and DOUBLE FOR THIS VERSION
OPTIONS = "\
-DCMAKE_INSTALL_PREFIX={0} \
-DCMAKE_INSTALL_BINDIR=bin.$SIMD_ARCH$ \
-DCMAKE_INSTALL_LIBDIR=lib.$SIMD_ARCH$ \
-DCMAKE_C_COMPILER=mpicc \
-DCMAKE_CXX_COMPILER=mpicxx \
-DGMX_OPENMP=ON \
-DGMX_MPI=$MPI$ \
-DGMX_GPU=OFF \
-DGMX_SIMD=$SIMD_ARCH$ \
-DGMX_USE_RDTSCP=$RDTSCP$ \
-DGMX_DOUBLE=$DOUBLE$ \
-DGMX_FFT_LIBRARY=fftw3 \
-DGMX_EXTERNAL_BLAS=OFF \
-DGMX_EXTERNAL_LAPACK=OFF \
-DBUILD_SHARED_LIBS=OFF \
-DGMX_PREFER_STATIC_LIBS=ON \
-DREGRESSIONTEST_DOWNLOAD=ON \
-DGMX_BUILD_MDRUN_ONLY=$MDRUN_ONLY$ \
-DGMX_DEFAULT_SUFFIX=OFF \
-DGMX_BINARY_SUFFIX=$BINARY_SUFFIX$ \
-DGMX_LIBS_SUFFIX=$LIBS_SUFFIX$ \
".format(GROMACS_INSTALL_PREFIX)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--archs', nargs='+')
    parser.add_argument('-md', '--mdrun_only', nargs='+')
    parser.add_argument('-r', '--rdtscp', nargs='+')
    parser.add_argument('-m', '--mpi', nargs='+')
    parser.add_argument('-g', '--gpu', nargs='+')
    parser.add_argument('-d', '--double', nargs='+')
    args = parser.parse_args()

    for (arch, mdrun_only, rdtscp, mpi, gpu, double) in zip(args.archs,
                                                            args.mdrun_only,
                                                            args.rdtscp,
                                                            args.mpi,
                                                            args.gpu,
                                                            args.double):
        cmake_options = ''
        cmake_options = OPTIONS.replace('$SIMD_ARCH$', arch)
        cmake_options = cmake_options.replace('$MDRUN_ONLY$', mdrun_only)
        cmake_options = cmake_options.replace('$RDTSCP$', rdtscp)
        cmake_options = cmake_options.replace('$MPI$', mpi)
        cmake_options = cmake_options.replace('$DOUBLE$', double)

        cmake_options = cmake_options.replace(
            '$BINARY_SUFFIX$',
            config.BINARY_SUFFIX.format(
                config.SUFFIX['mpi'][mpi],
                config.SUFFIX['double'][double],
                config.SUFFIX['rdtscp'][rdtscp],
            )
        )

        cmake_options = cmake_options.replace(
            '$LIBS_SUFFIX$',
            config.LIBRARY_SUFFIX.format(
                config.SUFFIX['mpi'][mpi],
                config.SUFFIX['double'][double],
                config.SUFFIX['rdtscp'][rdtscp],
            )
        )

        # configure and install
        build_dir = os.path.join(GROMACS_SOURCE_DIR, GROMACS_BUILD_DIR.format(arch))
        if os.path.exists(build_dir):
            os.system('rm -rf {0}'.format(
                os.path.join(build_dir, '*'))
            )
        else:
            os.mkdir(build_dir)

        os.chdir(build_dir)

        cmake_command = 'cmake {0} '.format(GROMACS_SOURCE_DIR)

        print(cmake_command + cmake_options + '\n')
        sys.stdout.flush()

        os.system(cmake_command + cmake_options)
        os.system('make -j {0} && make install'.format(JOBS))

        # create the wrapper
        wrapper = 'mdrun' if mdrun_only == 'ON' else 'gmx'

        wrapper = wrapper + config.WRAPPER_SUFFIX.format(
            config.SUFFIX['mpi'][mpi],
            config.SUFFIX['double'][double],
        )

        if not os.path.exists(os.path.join(BINARY, wrapper)):
            with open(os.path.join(BINARY, wrapper), 'w') as file:
                file.write(
                    "#!/usr/bin/env python\nimport sys,os\nos.system(\"gmx_chooser.py \" + ' '.join(sys.argv))\n"
                )

        # going back to the source directory again
        os.chdir(GROMACS_SOURCE_DIR)
