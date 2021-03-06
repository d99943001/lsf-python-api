#!/usr/bin/env python

# 
# (C) Copyright IBM Corporation 2013
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the Eclipse Public License.
# 
import os, sys
import time
from distutils.core import setup, Extension
from distutils.command.bdist_rpm import bdist_rpm
from distutils.command.install import INSTALL_SCHEMES

class bdist_rpm_custom(bdist_rpm):
      """bdist_rpm that sets custom RPM options"""
      def finalize_package_data (self):
            if self.release is None:
                  self.release = lsfversion
            if self.vendor is None:
                  self.vendor = 'IBM Corporation'
            if self.packager is None:
                  self.packager = 'IBM Corporation'
            # Disable autoreq in case LSF is installed from a tarball
            self.no_autoreq = 1
            bdist_rpm.finalize_package_data(self)

if os.uname()[0] == 'Linux' and os.uname()[4] == 'ppc64le' :
    found_xlc = False
    for path in os.environ["PATH"].split(os.pathsep):
        xlc_path = os.path.join(path, 'xlc')
        if os.access(xlc_path, os.F_OK):
            found_xlc = True
            os.environ["LDSHARED"]  = "%s -pthread -shared -Wl,-z,relro" % xlc_path
            break
    if found_xlc == False:
        print('''
Error: Cannot find IBM XL C/C++ compiler. To download and install the Community 
       Edition of the IBM XL C/C++ compiler at no charge, 
       refer to https://ibm.biz/BdYHna.
''')
        sys.exit()

if os.access(os.environ['LSF_LIBDIR'] + "/liblsbstream.a", os.F_OK):
    lsf_static_lib = [ os.environ['LSF_LIBDIR'] + '/liblsbstream.a']
    lsf_dynamic_lib = ['c', 'nsl', 'rt']
    warning_msg = ""
else:
    lsf_static_lib = []
    lsf_dynamic_lib = ['c', 'nsl', 'lsbstream', 'lsf', 'bat', 'rt']
    warning_msg = '''
Warning: The compatibility of the LSF Python API package is not guaranteed 
         if you update LSF at a later time. This is because your current 
         version of LSF does not release the
         %s/liblsbstream.a file.
         To avoid this compatibility issue, update LSF to version 10.1.0.3, 
         or later, then rebuild and reinstall the LSF Python API package. 
''' % (os.environ['LSF_LIBDIR'])

if sys.argv[1] == 'bdist_rpm' :
    lsidout = os.popen('lsid | head -1').readlines()
    lsfversion = lsidout[0].split()[4].split(',')[0]

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['platlib']

inc_path = os.path.abspath('pythonlsf')

if 'LSF_PYTHONAPI_INCPATH' not in os.environ:
    os.environ['LSF_PYTHONAPI_INCPATH'] = inc_path
else:
    inc_path = os.environ['LSF_PYTHONAPI_INCPATH']

setup(name='lsf-pythonapi',
      version='1.0.6',
      description='Python binding for IBM Spectrum LSF APIs',
      long_description='Python binding for IBM Spectrum LSF APIs',
      license='EPL',
      keywords='LSF,Grid,Cluster,HPC',
      url='https://github.com/IBMSpectrumComputing/lsf-python-api',
      ext_package='pythonlsf',
      data_files=[('pythonlsf', ['LICENSE'])],
      ext_modules=[Extension('_lsf', ['pythonlsf/lsf.i'],
                               include_dirs=['/usr/include/python2.4', inc_path],
                               library_dirs=[os.environ['LSF_LIBDIR']],
                               swig_opts=['-I' + os.environ['LSF_LIBDIR'] + '/../../include/lsf/', 
                                       #   '-DLSF_SIMULATOR',
                                          '-DOS_HAS_THREAD -D_REENTRANT'],
                               extra_compile_args=['-m64', 
                                    '-I' + os.environ['LSF_LIBDIR'] + '/../../include/lsf/', 
                                    '-Wno-strict-prototypes',
                                    '-DOS_HAS_THREAD -D_REENTRANT', #For multi-thread lib, lserrno
                                    '-Wp,-U_FORTIFY_SOURCE', #The flag needs -O option. Undefine it for warning.
                                    '-O0'], 
                               extra_link_args=['-m64'],
                               extra_objects=lsf_static_lib,
                               libraries=lsf_dynamic_lib)],
      py_modules=['pythonlsf.lsf'],
      cmdclass = { 'bdist_rpm': bdist_rpm_custom },
      classifiers=["Development Status :: 2 - Pre-Alpha",
                     "License :: OSI Approved :: Eclipse Public License",
                     "Operating System :: OS Independent",
                     "Programming Language :: Python",
                     "Topic :: Internet",
                     "Topic :: Scientific/Engineering",
                     "Topic :: Software Development",
                     "Topic :: System :: Distributed Computing",
                     "Topic :: Utilities",
                     ],
     )

if warning_msg :
    print(warning_msg)
