#!/usr/bin/env python

import argparse
import os
import sys

# Argument value for different option to choose from
ARCHITECTURES = ["sse2", "avx_256", "avx2_256", "avx_512"]
SWITCH = ['on', 'off']


def cli():
    parser = argparse.ArgumentParser(
        description='Parse user input for SIMD architecture from {0} and \
        switch on/off option for mdrun_only, rdtscp, mpi, precision and gpu and \
        then execute docker build command to build the docker image.'.format(
            str(ARCHITECTURES),
        ),
    )
    parser.add_argument(
        '-n',
        '--name',
        help='Name of the image to be built.',
        required=True
    )

    parser.add_argument(
        '-a',
        '--archs',
        help='White space separated list of SIMD instruction set.',
        nargs='+',
        choices=ARCHITECTURES,
        required=True
    )

    parser.add_argument(
        '-md',
        '--mdrun_only',
        help='Specify full or mdrun installtion.',
        nargs='+',
        choices=SWITCH,
        required=True
    )

    parser.add_argument(
        '-r',
        '--rdtscp',
        help='Specify rdtscp on/off. Default is {0}.'.format('on'),
        nargs='+',
        choices=SWITCH,
    )

    parser.add_argument(
        '-m',
        '--mpi',
        help='Specify mpi on/off. Default is {0}.'.format('off'),
        nargs='+',
        choices=SWITCH,
    )

    parser.add_argument(
        '-g',
        '--gpu',
        help='Specify gpu on/off. Default is {0}.'.format('off'),
        nargs='+',
        choices=SWITCH,
    )

    parser.add_argument(
        '-d',
        '--double',
        help='Specify precision double on/off. Default is {0}.'.format('off'),
        nargs='+',
        choices=SWITCH,
    )

    parser.add_argument(
        '-y',
        '--yes',
        help='Confirmation of Docker build.',
        action='store_true',
    )

    return (parser, parser.parse_args())


def display_configuration(args, architectures, mdrun_only, rdtscp, mpi, gpu, double):
    format_string = '{0!s:<15}{1!s:<15}{2!s:<15}{3!s:<15}{4!s:<15}{5!s:<15}'
    # print header
    print()
    print(format_string.format('Arch', 'mdrun_only', 'rdtscp', 'mpi', 'gpu', 'double'), end='\n')
    print('-' * 90)
    for i in range(len(architectures)):
        print(format_string.format(architectures[i], mdrun_only[i],
                                   rdtscp[i], mpi[i], gpu[i], double[i]), end='\n'
              )
    print('-' * 90)

    if not args.yes:
        confirmation = input(
            'Above GROMACS build configurations has provided. \
            \ngpu option currently not considered during GROMACS building. \
            \nType y/Y to proceed? Abot otherwise.\n'
        )
        if not confirmation in ['y', 'Y']:
            print('Aborting...')
            sys.exit()

# Configurating optional arguments


def configure_optional_arguments(expected_arg_length, provided_args, *, default='ON'):
    args = [default] * expected_arg_length
    if provided_args:
        min_length = min(expected_arg_length, len(provided_args))
        args[:min_length] = [r.upper() for r in provided_args[:min_length]]

    return args


if __name__ == '__main__':

    parser, args = cli()

    if len(args.mdrun_only) < len(args.archs):
        parser.error('Missing mdrun_only option for one or more architectures.')
    else:
        #  Parsing input
        archs = args.archs
        mdrun_only = [r.upper() for r in args.mdrun_only[:len(archs)]]

        rdtscp = configure_optional_arguments(len(archs), args.rdtscp)
        mpi = configure_optional_arguments(len(archs), args.mpi, default='OFF')
        gpu = configure_optional_arguments(len(archs), args.gpu, default='OFF')
        double = configure_optional_arguments(len(archs), args.double, default='OFF')

        # removing duplicate configuration
        configs = list(set(zip(archs, mdrun_only, rdtscp, mpi, gpu, double)))
        archs, mdrun_only, rdtscp, mpi, gpu, double = [
            [conf[i] for conf in configs]
            for i in range(6)
        ]

        # displaying configuration ask for confirmation
        display_configuration(args, archs, mdrun_only, rdtscp, mpi, gpu, double)

        docker_build_command = 'docker build --build-arg ARCHITECTURES="{0}"'.format(' '.join(archs),) + \
            ' --build-arg MDRUN_ONLY="{0}" --build-arg RDTSCP="{1}"'.format(' '.join(mdrun_only),
                                                                            ' '.join(rdtscp)
                                                                            ) + \
            ' --build-arg MPI="{0}" --build-arg GPU="{1}" --build-arg DOUBLE="{2}" -t {3} ..'.format(
            ' '.join(mpi),
            ' '.join(gpu),
            ' '.join(double),
            args.name
        )

        print('Docker build command: ', docker_build_command, sep='\n')

        os.system(docker_build_command)
