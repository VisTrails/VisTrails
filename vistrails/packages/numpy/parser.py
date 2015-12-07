#!/usr/bin/env python
###############################################################################
##
## Copyright (C) 2014-2015, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

from __future__ import division


import importlib
import os.path

from vistrails.core.wrapper.diff import apply_diff
from vistrails.core.wrapper.specs import SpecList, ClassSpec, \
    FunctionSpec
from vistrails.core.wrapper.python_parser import PythonParser

import numpy as np
import numpy.matlib


def parser():
    parser = PythonParser(instance_type='basic:List')
    this_dir = os.path.dirname(os.path.realpath(__file__))

    ##########################################################################
    # wrap classes

    class_spec_name = os.path.join(this_dir,'classes.xml')
    raw_class_spec_name = class_spec_name[:-4] + '-raw.xml'
    class_spec_diff = class_spec_name[:-4] +  '-diff.xml'

    # generate specs
    classes = []
    class_names = []
    functions = []
    func_names = []
    def add(base, clist, namespace):
        if isinstance(clist, basestring):
            clist = clist.split(',')
        for c in clist:
            klass = base + '.' + c
            if klass in class_names:
                print "Skipping duplicate:", klass
                continue
            class_names.append(klass)
            classes.append(parser.parse_class(klass,
                                              namespace=namespace,
                                              attribute_parsing=False))
            inspector = parser.parse_class(klass,
                                           name=c+'Inspector',
                                           namespace=namespace,
                                           argument_parsing=False)
            if (len(inspector.input_port_specs) > 1 or
                len(inspector.output_port_specs) > 1):
                classes.append(inspector)
            for f in parser.parse_class_methods(klass,
                                         namespace=namespace+'|'+c+'Methods'):
                fname = (f.namespace, f.module_name)
                if fname in func_names:
                    print "Skipping duplicate:", fname
                    continue
                func_names.append(fname)
                functions.append(f)

    poly_libs = ['numpy.polynomial.' + m for m in
        'polynomial,chebyshev,legendre,laguerre,hermite,hermite_e'.split(',')]

    def add_all(lib):
        m = importlib.import_module(lib)
        to_add = []
        for f in (m.__all__ if hasattr(m,'__all__') else
                [s for s in dir(m) if not s.startswith('_')]):
            try:
                typename = type(getattr(m, f)).__name__
                if typename in ['type', 'ABCMeta']:
                    to_add.append(f)
                #else:
                #    print "Skipped non-class: %s(%s)" % (f, typename)
            except AttributeError:
                print "No such class:", f
        add(lib, to_add, lib.split('.', 1)[-1].replace('.','|'))

    add('numpy', 'ndarray', namespace='array')
    dtypes = [np.bool_,
              np.int8, np.int16, np.int32, np.int64,
              np.uint8, np.uint16, np.uint32, np.uint64,
              np.float16, np.float32, np.float64,
              np.complex64, np.complex128]
    for dtype in dtypes:
        classes.extend([parser.parse_class(dtype, namespace='dtypes')])
    for lib in poly_libs:
        add_all(lib)
    add_all('numpy.ma')

    class_list = SpecList(classes)
    class_list.write_to_xml(raw_class_spec_name)
    apply_diff(ClassSpec, raw_class_spec_name, class_spec_diff, class_spec_name)


    ##########################################################################
    # wrap functions

    fun_spec_name = os.path.join(this_dir, 'functions.xml')
    raw_fun_spec_name = fun_spec_name[:-4] + '-raw.xml'
    fun_spec_diff = fun_spec_name[:-4] + '-diff.xml'

    # generate specs
    def add(base, flist, namespace):
        if isinstance(flist, basestring):
            flist = flist.split(',')
        for f in flist:
            functions.append(parser.parse_function(base + '.' + f,
                                                   namespace=namespace))

    def add_all(lib):
        m = importlib.import_module(lib)
        to_add = []
        for f in (m.__all__ if hasattr(m,'__all__') else
                [s for s in dir(m) if not s.startswith('_')]):
            try:
                typename = type(getattr(m, f)).__name__
                if 'function' in typename:
                    to_add.append(f)
                #else:
                #    print "Skipped non-function: %s(%s)" % (f, typename)
            except AttributeError:
                print "No such function:", f
        add(lib, to_add, lib.split('.', 1)[-1].replace('.', '|'))

    def add_f(flist, namespace):
        for f in flist:
            functions.append(parser.parse_function(f, namespace=namespace))

    add_f([np.ravel, np.swapaxes, np.transpose,
           np.atleast_1d, np.atleast_2d, np.atleast_3d,
           np.array, np.zeros, np.empty, np.asarray,
           np.concatenate, np.stack, np.column_stack, np.dstack, np.hstack,
           np.vstack,
           np.split, np.array_split,
           np.tile, np.repeat, np.delete, np.insert, np.append, np.resize,
           np.trim_zeros, np.unique,
           np.fliplr, np.flipud, np.reshape, np.roll, np.rot90], 'array')

    add_f([np.asmatrix, np.bmat,
           np.matlib.empty, np.matlib.zeros, np.matlib.ones, np.matlib.eye,
           np.matlib.identity, np.matlib.repmat, np.matlib.rand, np.matlib.randn
           ], 'matrix')

    add_f(['numpy.' + f for f in ['bitwise_and', 'bitwise_or',
           'bitwise_xor', 'invert', 'left_shift', 'right_shift',
           'packbits', 'unpackbits', 'binary_repr']], 'binary')

    add_f([np.load, np.save, np.savez, np.savez_compressed,
           np.loadtxt, np.savetxt, np.genfromtxt, np.fromregex,
           np.fromstring, np.fromfile, np.array2string,
           np.array_repr, np.array_str, np.memmap], 'io')

    # add_f([np.dot, np.vdot, np.inner, np.outer, np.matmul,
    #        np.tensordot, np.einsum, np.linalg.matrix_power,
    #        np.kron, np.linalg.cholesky, np.linalg.qr, np.linalg.svd,
    #        np.linalg.eig, np.linalg.eigh, np.linalg.eigvals,
    #        np.linalg.eigvalsh, np.linalg.norm, np.linalg.cond,
    #        np.linalg.det, np.linalg.matrix_rank, np.linalg.slogdet,
    #        np.trace, np.linalg.solve, np.linalg.tensorsolve,
    #        np.linalg.lstsq, np.linalg.inv,
    #        np.linalg.pinv, np.linalg.tensorinv], 'linalg')

    add_f([np.dot, np.vdot, np.inner, np.outer, np.matmul,
           np.tensordot, np.einsum, np.trace], 'linalg')

    # add_f([np.fft.fft, np.fft.ifft, np.fft.fft2, np.fft.ifft2,
    #        np.fft.fftn, np.fft.ifftn, np.fft.rfft, np.fft.irfft,
    #        np.fft.rfft2, np.fft.irfft2, np.fft.rfftn, np.fft.irfftn,
    #        np.fft.hfft, np.fft.ihfft,
    #        np.fft.fftfreq, np.fft.rfftfreq, np.fft.fftshift, np.fft.ifftshift
    #        ], 'fft')

    add_f([np.fv, np.pv, np.npv, np.pmt, np.ppmt, np.ipmt, np.irr, np.mirr,
           np.nper, np.rate], 'fft')

    add_f(['numpy.' + f for f in (
        'all,any,isfinite,isinf,isnan,isneginf,isposinf,iscomplex,'
        'iscomplexobj,isfortran,isreal,isrealobj,isscalar,logical_and,'
        'logical_or,logical_not,logical_xor,allclose,isclose,array_equal,'
        'array_equiv,greater,greater_equal,less,less_equal,equal,not_equal'
        ).split(',')], 'logic')

    add_f(['numpy.' + f for f in ('sin,cos,tan,arcsin,arccos,arctan,hypot,'
        'arctan2,degrees,radians,unwrap,deg2rad,rad2deg,sinh,cosh,arcsinh,'
        'arccosh,arctanh,around,round_,rint,fix,floor,ceil,trunc,prod,sum,'
        'nansum,cumprod,cumsum,diff,ediff1d,gradient,cross,trapz,'
        'exp,expm1,exp2,log,log10,log2,log1p,logaddexp,logaddexp2,'
        'i0,sinc,signbit,copysign,frexp,ldexp,'
        'add,reciprocal,negative,multiply,divide,power,subtract,true_divide,'
        'floor_divide,fmod,mod,modf,remainder,'
        'angle,real,imag,conj,convolve,clip,sqrt,square,absolute,fabs,sign,'
        'maximum,fmax,fmin,nan_to_num,real_if_close,interp').split(',')], 'math')


    # add_f(['numpy.random.' + f for f in (
    #        'pareto,permutation,poisson,power,beta,binomial,rand,bytes,randint,'
    #        'chisquare,randn,choice,random,dirichlet,random_integers,division,'
    #        'random_sample,exponential,ranf,rayleigh,gamma,sample,geometric,seed,'
    #        'get_state,set_state,gumbel,shuffle,hypergeometric,standard_cauchy,'
    #        'standard_exponential,laplace,standard_gamma,logistic,standard_normal,'
    #        'lognormal,standard_t,logseries,test,mtrand,triangular,multinomial,'
    #        'uniform,multivariate_normal,vonmises,negative_binomial,wald,'
    #        'noncentral_chisquare,warnings,noncentral_f,weibull,normal,zipf'
    #         ).split(',')], 'random')

    add_f(['numpy.' + f for f in (
           'sort,lexsort,argsort,msort,sort_complex,partition,'
           'argpartition,argmax,nanargmax,argmin,nanargmin,argwhere,nonzero,'
           'where,searchsorted,extract,count_nonzero'
            ).split(',')], 'sort')

    add_f(['numpy.' + f for f in (
           'amin,amax,nanmin,nanmax,ptp,percentile,nanpercentile,'
           'median,average,mean,std,var,nanmedian,nanmean,nanstd,nanvar,'
           'corrcoef,correlate,cov,'
           'histogram,histogram2d,histogramdd,bincount,digitize'
            ).split(',')], 'statistics')


    for L in 'linalg,fft,random'.split(','):
        add_all('numpy.' + L)
    for lib in poly_libs:
        add_all(lib)
    add_all('numpy.ma')

    fun_list = SpecList(functions)
    fun_list.write_to_xml(raw_fun_spec_name)
    apply_diff(FunctionSpec, raw_fun_spec_name, fun_spec_diff, fun_spec_name)
    return class_list, fun_list

if __name__ == '__main__':
    parser()
