#!/usr/bin/env python
import sys
import os
from subprocess import Popen, PIPE, call
import config


ARCHITECTURES = [' avx_512 ', ' avx2 ', ' avx ', ' sse2 ']
BINARY_SUFFIX = ['avx_512', 'avx2_256', 'avx_256', 'sse2']

RDTSCP = 'rdtscp'


# Gromacs installation directory : These should go to the common file
GROMACS_INATALL_DIR = '/gromacs'
GROMACS_BINDIR = os.path.join(GROMACS_INATALL_DIR, 'bin.{0}')

# Checking whether a file is executable or not


def is_executable(file):
    acl = os.popen('ls -l ' + file).read()[0:10]
    if acl.count('x') == 3:
        return True

    return False


# Choose the best possible GROMACS based on cpu's SIMD instruction
def get_binary_directory(flags, gmx):
    for (index, (arch, bin_suffix)) in enumerate(zip(ARCHITECTURES, BINARY_SUFFIX)):
        bin_dir = GROMACS_BINDIR.format(bin_suffix)
        if arch in flags and os.path.exists(bin_dir):
            fileshere = os.listdir(bin_dir)
            try:
                idx = fileshere.index(gmx)
            except ValueError:
                continue
            else:
                file = fileshere[idx]
                if is_executable(os.path.join(bin_dir, file)):
                    return (index, bin_dir)
                else:
                    continue
    return (None, None)


def run(binary_directory, gmx, args):
    binary_path = os.path.join(binary_directory, gmx)
    os.system(binary_path + ' ' + ' '.join(args))


def get_possible_gmx_directory(flags, gmx, chosen_dir, chosen_gmx, chosen_args):
    binary_directory = get_binary_directory(flags=flags, gmx=gmx)
    if binary_directory[1]:
        if chosen_gmx:
            if chosen_dir[0] > binary_directory[0]:
                return (binary_directory, gmx, sys.argv[2:])
            else:
                return (chosen_dir, chosen_gmx, chosen_args)
        else:
            return (binary_directory, gmx, sys.argv[2:])
    else:
        return (chosen_dir, chosen_gmx, chosen_args)


if __name__ == '__main__':
    sys.argv[1] = os.path.split(sys.argv[1])[1]

    pipe = Popen('cat /proc/cpuinfo | grep ^flags | head -1', stdout=PIPE, shell=True)
    flags = pipe.communicate()[0]

    rdtscp_enabled = True if RDTSCP in flags else False

    gromacs = [sys.argv[1]]

    if 'mdrun' in sys.argv or 'mdrun_mpi' in sys.argv:
        if sys.argv[1].startswith('mdrun'):
            gromacs.append(gromacs[0].replace('mdrun', 'gmx'))
        elif sys.argv[1].startswith('gmx'):
            if len(sys.argv) > 2 and sys.argv[2].startswith('mdrun'):
                gromacs.append(gromacs[0].replace('gmx', 'mdrun'))

    if rdtscp_enabled:
        gromacs_rdtscp = [gmx + config.SUFFIX['rdtscp']['ON'] for gmx in gromacs]
        gromacs = gromacs_rdtscp + gromacs

    chosen_dir, chosen_gmx, chosen_args = None, None, None
    for gmx in gromacs:
        (chosen_dir, chosen_gmx, chosen_args) = get_possible_gmx_directory(flags, gmx, chosen_dir, chosen_gmx, chosen_args)

    if not chosen_gmx:
        print('No appropriate GROMACS installaiton available. Exiting...')
        sys.exit()

    if sys.argv[1].startswith('gmx'):
        # remove subcommand  'mdrun' from gmx and gmx_mpi
        if len(sys.argv) > 2 and chosen_gmx.startswith('mdrun'):
            del chosen_args[0]
    elif sys.argv[1].startswith('mdrun'):
        # add subcommand  'mdrun' to gmx and gmx_mpi
        if chosen_gmx.startswith('gmx'):
            chosen_args.insert(0, 'mdrun')

    # running the binary
    run(binary_directory=chosen_dir[1], gmx=chosen_gmx, args=chosen_args)
