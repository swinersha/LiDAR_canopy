import numpy as np
# This function calculates best fitting polynomial line (up to order 3) for a
# given set of input points x and y, using linear least squares inversion.
# Default is for 1st order.
# x and y are one dimensional arrays
def oneD_least_squares_polynomial(x,y,order=1):
    # first up - mask nodata values
    mask = np.isfinite(y)
    X = x[mask]
    Y = y[mask]
    ones = np.ones(Y.size)
    A=np.array([])
    
    if order == 1:
        # coefficients returned should be in order a-b for:
        # z = ax + b
        A = np.array([X,ones]).T
    elif order == 2:
        # coefficients returned should be in order a-c for:
        # z = ax^2 + bx + c
        A = np.array([X**2, X, ones]).T
    elif order == 3:
        # coefficients returned should be in order a-d for:
        # z = ax^3 + bx^2 + cx + d
        A = np.array([X**3, X**2, X, ones]).T
    elif order == 4:
        # coefficients returned should be in order a-e for:
        # z = ax^4 + bx^3 + cx^2 + dx + e
        A = np.array([X**4, X**3, X**2, X, ones]).T
    b = Y.copy()
    coeff, r, rank, s = np.linalg.lstsq(A, b)
    return coeff

# This function calculates best fitting polynomial surface (up to order 3) for a
# given set of input points x,y and z, using linear least squares inversion.
# Default is for 1st order.
# x,y and z are one dimensional arrays
def twoD_least_squares_polynomial(x,y,z,order=1):
    # first up - mask nodata values
    mask = np.isfinite(z)
    X = x[mask]
    Y = y[mask]
    Z = z[mask]
    ones = np.ones(Z.size)
    A=np.array([])
    
    if order == 1:
        # coefficients returned should be in order a-f for:
        # z = ax + by + c
        A = np.array([X,Y,ones]).T
    elif order == 2:
        # coefficients returned should be in order a-f for:
        # z = ax^2 + by^2 + cxy + dx + ey + f
        A = np.array([X**2, Y**2, X*Y, X, Y, ones]).T
    elif order == 3:
        # coefficients returned should be in order a-j for:
        # z = ax^3 + by^3 + cyx^2 + dxy^2 + ex^2 + fy^2 + gxy + hx + iy + j
        A = np.array([X**3, Y**3, X**2*Y, Y**2*X, X**2, Y**2, X*Y, X, Y, ones]).T
    b = Z.copy()
    coeff, r, rank, s = np.linalg.lstsq(A, b)
    return coeff
