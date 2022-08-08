# -*- coding: utf-8 -*-
"""
Created:  Thu Jun 16 12:29:52 2022
Author:   wroser
=============================================================================
Description:

"""

# %% Imports
import numpy as np
from sympy import symbols, solveset, factorial, S, Poly
import scipy.special as sps

# %% Code
def gauss_lobatto(N):
    '''
    Reference: https://en.wikipedia.org/wiki/Legendre_polynomials
               https://en.wikipedia.org/wiki/Gaussian_quadrature#Gauss%E2%80%93Lobatto_rules
    Note: Stops working after about 50 nodes.
               
    Parameters
    ----------
    N : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    
    n = N - 1
    
    x = symbols('x', real=True)
    f1 = (x**2 - 1)**n
    f2 = f1.diff(x, n)
    f3 = 1/2**n / factorial(n) * f2 # Legendre polynomial P_n-1
    f4 = f3.diff(x, 1)
    
    # Solve f4 to get gauss-lobatto points
    # Option 1: SymPy
    # xs = list(solveset(f4, x, domain=S.Reals)) # Note: Much faster than solve.
    # Option 2: Numpy
    f5 = Poly(f4) # convert dtype
    coeffs = f5.all_coeffs()
    xs = list(np.roots(coeffs))
    
    xs.insert(0, -1.0)
    xs.append(1.0)
    xs = np.asarray(xs)
    xs = np.real(xs) # Legendre polynomial has all real roots, but solver is 
                     # approximate and may have near zero imaginary values.
    xs = xs.astype(float)
    
    # Weights
    # Note: Declaration that x != +/-1 for w function is incorrect on both
    #       Wikipedia and original 1972 source.
    w = np.zeros(N)
    for i in range(N):
        w[i] = 2 / (N*(N-1)* (f3.subs(x, xs[i]))**2)
    
    # Rearrange to get correct order
    ind = np.argsort(xs)
    xs = xs[ind]
    w = w[ind]
    
    return (xs, w)

def bisect(fn, a, b, tolerance=1e-14):
    '''
    Finds function zero between a and b using bisection method.

    Parameters
    ----------
    fn : TYPE
        DESCRIPTION.
    a : TYPE
        DESCRIPTION.
    b : TYPE
        DESCRIPTION.
    tolerance : TYPE, optional
        DESCRIPTION. The default is 1e-14.

    Returns
    -------
    x_mid : TYPE
        DESCRIPTION.

    '''
    assert np.sign(fn(a)) != np.sign(fn(b))
    while b-a > tolerance:
        x_mid = a + (b-a)/2
        if np.sign(fn(a)) != np.sign(fn(x_mid)):
            b = x_mid
        else:
            a = x_mid
    return x_mid

def eval_legendre_deriv(n, x):
    '''
    Source: https://relate.cs.illinois.edu/course/CS450-S20/f/demos/upload/quadrature_and_diff/Gaussian%20quadrature%20weight%20finder.html

    Needed for next function.

    '''
    return (
        (x*sps.eval_legendre(n, x) - sps.eval_legendre(n-1, x))
        /
        ((x**2-1)/n))


def bisection(f, a, b, tol=1e-14):
    assert np.sign(f(a)) != np.sign(f(b))
    while b-a > tol:
        m = a + (b-a)/2
        fm = f(m)
        if np.sign(f(a)) != np.sign(fm):
            b = m
        else:
            a = m
            
    return m

def gauss_lobatto2(N):
    '''
    Reference: https://relate.cs.illinois.edu/course/CS450-S20/f/demos/upload/quadrature_and_diff/Gaussian%20quadrature%20weight%20finder.html
    Usually accurate to about 13 decimal places. More stable and conistent than above.
    
    Parameters
    ----------
    N : int; number of gauss integration points

    Returns
    -------
    tuple of lists

    '''
    nodes = sps.legendre(N).weights[:, 0]
    brackets = sps.legendre(N-1).weights[:, 0]

    nodes = np.zeros(N)
    nodes[0] = -1
    nodes[-1] = 1
    
    from functools import partial
    
    # Use the fact that the roots of P_{n-1} bracket the roots of P_{n-1}':
    for i in range(N-2):
        nodes[i+1] = bisect(
            partial(eval_legendre_deriv, N-1),
            brackets[i], brackets[i+1])
    
    # Weights - same as before
    n = N - 1
    
    x = symbols('x', real=True)
    f1 = (x**2 - 1)**n
    f2 = f1.diff(x, n)
    f3 = 1/2**n / factorial(n) * f2
    
    w = np.zeros(N)
    for i in range(N):
        w[i] = 2 / (N*(N-1)* (f3.subs(x, nodes[i]))**2)
    
    # Rearrange to get correct order
    ind = np.argsort(nodes)
    nodes = nodes[ind]
    w = w[ind]
    
    return (nodes, w)

def gl_length(length, N, dist_function=gauss_lobatto2):
    '''
    Returns gauss-lobatto nodes and weights along a nonstandard length.

    Parameters
    ----------
    length : float
        Output will provide nodes from -length/2 to length/2.
    N : int
        Number of nodes and weights.

    Returns
    -------
    tuple of numpy arrays: (nodes, weights)

    '''
    
    x, w = dist_function(N)
    x = length/2 * x
    w = length/2 * w
    
    return (x, w)

def gl_area(width, N1, depth, N2, dist_function=gauss_lobatto2):
    
    # Linear nodes and weights
    x, wx = gl_length(width, N1, dist_function)
    y, wy = gl_length(depth, N2, dist_function)
    
    # Convert to matrix
    wx = wx[np.newaxis]
    wy = wy[np.newaxis]
    areas = wx.T @ wy
    
    return x, y, areas

def linear(N):
    
    xs = np.zeros(N)
    for i in range(len(xs)):
        xs[i] = -1 + 1/N + 2/N*i
    w = np.full(N, 2/N)
    return (xs, w)

if __name__ == '__main__':
    
    pass
