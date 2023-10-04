# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

from spack import *
from spack.util.environment import EnvironmentModifications


class Imod(Package):
    """IMOD is a set of image processing, modeling and display programs used for tomographic
    reconstruction and for 3D reconstruction of EM serial sections and optical sections. The
    package contains tools for assembling and aligning data within multiple types and sizes
    of image stacks, viewing 3-D data from any orientation, and modeling and display of the
    image files. IMOD was developed primarily by David Mastronarde, Rick Gaudette, Sue Held,
    Jim Kremer, Quanren Xiong, Suraj Khochare, and John Heumann at the University of Colorado."""

    homepage = "https://bio3d.colorado.edu/imod/"

    version('4.11.24', sha256='7d128a0f0fda4bbb79bd75823e9242ffb548c9c596a27b3ce92e0dfd790dfaff',
             url='https://bio3d.colorado.edu/imod/AMD64-RHEL5/imod_4.11.24_RHEL7-64_CUDA10.1.sh', expand=False)

    depends_on('python')
    depends_on('java')
    depends_on('mesa-glu')

    @run_before('install')
    def expand_file(self):
        bash = which('bash')
        bash(self.stage.archive_file, '-extract')

    def install(self, spec, prefix):
        with working_dir(join_path(self.stage.source_path,'IMODtempDir')):
            python(join_path(self.stage.source_path,'IMODtempDir/installIMOD'), '-dir', '{0}'.format(prefix), '-skip')
        mkdir(prefix.ImodCalib)
        with working_dir(join_path(prefix, 'ImodCalib')):
            with open('cpu.adoc', 'w') as f:
                f.write("""\
# See https://bio3d.colorado.edu/imod/doc/man/cpuadoc.html
# and https://bio3d.colorado.edu/imod/nightlyBuilds/IMOD/autodoc/cpu.adoc
# for details and other ways parallel processes through Etomo
# can be implemented (e.g. for standalone computers or pbs, pbs-maui,
# or sge cluster queues)
Version = 1.2
#
[Queue = CPU]
# make the cpu partition available
command = queuechunk -t slurm -l -n1,-c1,--partition=cpu
number = 128
#
[Queue = GPU]
# schedule jobs for the gpu partition
gpu = 1
command = queuechunk -t slurm -l -n1,-c1,--gres=gpu:2,--partition=gpu""")

    def setup_run_environment(self, env):
        env.set('IMOD_DIR', self.prefix.join('IMOD'))
        filename = self.prefix.join('IMOD/IMOD-linux.sh')
        env.extend(EnvironmentModifications.from_sourcing_file(filename))
        env.set('IMOD_CALIB_DIR', self.prefix.join('ImodCalib'))
