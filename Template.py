# https://weber.itn.liu.se/~stegu/simplexnoise/SimplexNoise.java

from pprint import pprint
import math
import random


class SimplexNoiseClass():
    def __init__(self, seed=0):
        self.grad3 = [
            1, 1, 0,
            -1, 1, 0,
            1, -1, 0,

            -1, -1, 0,
            1, 0, 1,
            -1, 0, 1,

            1, 0, -1,
            -1, 0, -1,
            0, 1, 1,

            0, -1, 1,
            0, 1, -1,
            0, -1, -1
        ]

        self.grad4 = [
            0, 1, 1, 1,
            0, 1, 1, -1,
            0, 1, -1, 1,
            0, 1, -1, -1,

            0, -1, 1, 1,
            0, -1, 1, -1,
            0, -1, -1, 1,
            0, -1, -1, -1,

            1, 0, 1, 1,
            1, 0, 1, -1,
            1, 0, -1, 1,
            1, 0, -1, -1,

            -1, 0, 1, 1,
            -1, 0, 1, -1,
            -1, 0, -1, 1,
            -1, 0, -1, -1,

            1, 1, 0, 1,
            1, 1, 0, -1,
            1, -1, 0, 1,
            1, -1, 0, -1,

            -1, 1, 0, 1,
            -1, 1, 0, -1,
            -1, -1, 0, 1,
            -1, -1, 0, -1,

            1, 1, 1, 0,
            1, 1, -1, 0,
            1, -1, 1, 0,
            1, -1, -1, 0,

            -1, 1, 1, 0,
            -1, 1, -1, 0,
            -1, -1, 1, 0,
            -1, -1, -1, 0
        ]

        self.permutation = []
        period = 256
        if seed is not None:
            random.seed(seed)
        __permutation = list(range(period))
        for i in list(__permutation):
            j = random.randint(0, period - 1)
            __permutation[i], __permutation[j] = __permutation[j], __permutation[i]
        self.permutation = __permutation * 2

        # To remove the need for index wrapping, double the permutation table length
        self.perm = [0] * 512
        self.permMod12 = [0] * 512
        for i in range(512):
            self.perm[i] = self.permutation[i & 255]
            self.permMod12[i] = (self.perm[i] % 12)

        # Skewing and unskewing factors for 2, 3, and 4 dimensions
        self.F2 = 0.5 * (math.sqrt(3.0) - 1.0)
        self.G2 = (3.0 - math.sqrt(3.0)) / 6.0
        self.F3 = 1.0 / 3.0
        self.G3 = 1.0 / 6.0
        self.F4 = (math.sqrt(5.0) - 1.0) / 4.0
        self.G4 = (5.0 - math.sqrt(5.0)) / 20.0

    # 2D simplex noise
    def noise2d(self, x=0.0, y=0.0):
        # Noise contributions from the three corners
        n0 = 0.0
        n1 = 0.0
        n2 = 0.0
        # Skew the input space to determine which simplex cell we're in
        # Hairy factor for 2D
        s = (x + y) * self.F2
        i = math.floor(x + s)
        j = math.floor(y + s)
        t = (i + j) * self.G2
        # Unskew the cell origin back to (x, y) space
        X0 = i - t
        Y0 = j - t
        # The x, y distances from the cell origin
        x0 = x - X0
        y0 = y - Y0
        # For the 2D case, the simplex shape is an equilateral triangle.
        # Determine which simplex we are in.
        # Offsets for second (middle) corner of simplex in (i,j) coords
        i1 = 0
        j1 = 0
        # lower triangle, XY order: (0, 0) -> (1, 0) -> (1, 1)
        if(x0 > y0):
            i1 = 1
            j1 = 0
        else:
            # upper triangle, YX order: (0, 0) -> (0, 1) -> (1, 1)
            i1 = 0
            j1 = 1
        # A step of (1, 0) in (i, j) means a step of (1 - c, -c) in (x, y), and
        # a step of (0, 1) in (i, j) means a step of (-c, 1 - c) in (x, y), where
        # c = (3 - sqrt(3)) / 6
        # Offsets for middle corner in (x,y) unskewed coords
        x1 = x0 - i1 + self.G2
        y1 = y0 - j1 + self.G2
        # Offsets for last corner in (x,y) unskewed coords
        x2 = x0 - 1.0 + 2.0 * self.G2
        y2 = y0 - 1.0 + 2.0 * self.G2
        # Work out the hashed gradient indices of the three simplex corners
        ii = int(i) & 255
        jj = int(j) & 255
        gi0 = int(self.permMod12[ii + self.perm[jj]])
        gi1 = int(self.permMod12[ii + i1 + self.perm[jj + j1]])
        gi2 = int(self.permMod12[ii + 1 + self.perm[jj + 1]])
        # Calculate the contribution from the three corners
        t0 = 0.5 - x0 * x0 - y0 * y0
        if t0 >= 0:
            gi0 = self.permMod12[ii + self.perm[jj]] * 3
            t0 *= t0
            n0 = t0 * t0 * (self.grad3[gi0] * x0 + self.grad3[gi0 + 1] * y0)

        t1 = 0.5 - x1 * x1 - y1 * y1
        if t1 >= 0:
            gi1 = self.permMod12[ii + i1 + self.perm[jj + j1]] * 3
            t1 *= t1
            n1 = t1 * t1 * (self.grad3[gi1] * x1 + self.grad3[gi1 + 1] * y1)

        t2 = 0.5 - x2 * x2 - y2 * y2
        if t2 >= 0:
            gi2 = self.permMod12[ii + 1 + self.perm[jj + 1]] * 3
            t2 *= t2
            n2 = t2 * t2 * (self.grad3[gi2] * x2 + self.grad3[gi2 + 1] * y2)

        # Add contributions from each corner to get the final noise value.
        # The result is scaled to return values in the interval [-1,1].
        return 70.0 * (n0 + n1 + n2)


    # 3D simplex noise
    def noise3d(self, x=0.0, y=0.0, z=0.0):
        # Noise contributions from the four corners
        n0 = 0.0
        n1 = 0.0
        n2 = 0.0
        n3 = 0.0
        # Skew the input space to determine which simplex cell we're in
        # Very nice and simple skew factor for 3D
        s = (x + y + z) * self.F3
        i = math.floor(x + s)
        j = math.floor(y + s)
        k = math.floor(z + s)
        t = (i + j + k) * self.G3
        # Unskew the cell origin back to (x,y,z) space
        X0 = i - t
        Y0 = j - t
        Z0 = k - t
        # The x, y, z distances from the cell origin
        x0 = x - X0
        y0 = y - Y0
        z0 = z - Z0
        # For the 3D case, the simplex shape is a slightly irregular tetrahedron.
        # Determine which simplex we are in.
        # Offsets for second corner of simplex in (i,j,k) coords
        # Offsets for third corner of simplex in (i,j,k) coords
        i1 = 0
        j1 = 0
        k1 = 0
        i2 = 0
        j2 = 0
        k2 = 0
        if x0 >= y0:
            # X Y Z order
            if y0 >= z0:
                i1 = 1
                j1 = 0
                k1 = 0
                i2 = 1
                j2 = 1
                k2 = 0
            # X Z Y order
            elif x0 >= z0:
                i1 = 1
                j1 = 0
                k1 = 0
                i2 = 1
                j2 = 0
                k2 = 1
            # Z X Y order
            else:
                i1 = 0
                j1 = 0
                k1 = 1
                i2 = 1
                j2 = 0
                k2 = 1
        # x0 < y0
        else:
            # Z Y X order
            if y0 < z0:
                i1 = 0
                j1 = 0
                k1 = 1
                i2 = 0
                j2 = 1
                k2 = 1
            # Y Z X order
            elif x0 < z0:
                i1 = 0
                j1 = 1
                k1 = 0
                i2 = 0
                j2 = 1
                k2 = 1
            # Y X Z order
            else:
                i1 = 0
                j1 = 1
                k1 = 0
                i2 = 1
                j2 = 1
                k2 = 0

        # A step of (1, 0, 0) in (i, j, k) means a step of (1 - c, -c, -c) in (x, y, z),
        # a step of (0, 1, 0) in (i, j, k) means a step of (-c, 1 - c, -c) in (x, y, z), and
        # a step of (0, 0, 1) in (i, j, k) means a step of (-c, -c, 1 - c) in (x, y, z), where
        # c = 1 / 6.
        # Offsets for second corner in (x, y, z) coords
        x1 = x0 - i1 + self.G3
        y1 = y0 - j1 + self.G3
        z1 = z0 - k1 + self.G3
        # Offsets for third corner in (x, y, z) coords
        x2 = x0 - i2 + 2.0 * self.G3
        y2 = y0 - j2 + 2.0 * self.G3
        z2 = z0 - k2 + 2.0 * self.G3
        # Offsets for last corner in (x, y, z) coords
        x3 = x0 - 1.0 + 3.0 * self.G3
        y3 = y0 - 1.0 + 3.0 * self.G3
        z3 = z0 - 1.0 + 3.0 * self.G3
        # Work out the hashed gradient indices of the four simplex corners
        ii = int(i) & 255
        jj = int(j) & 255
        kk = int(k) & 255

        # Calculate the contribution from the four corners
        t0 = 0.6 - x0 * x0 - y0 * y0 - z0 * z0
        if t0 < 0:
            n0 = 0.0
        else:
            gi0 = self.permMod12[ii + self.perm[jj + self.perm[kk]]] * 3
            t0 *= t0
            n0 = t0 * t0 * (self.grad3[gi0] * x0 + self.grad3[gi0 + 1] * y0 + self.grad3[gi0 + 2] * z0)

        t1 = 0.6 - x1 * x1 - y1 * y1 - z1 * z1
        if t1 < 0:
            n1 = 0.0
        else:
            gi1 = self.permMod12[ii + i1 + self.perm[jj + j1 + self.perm[kk + k1]]] * 3
            t1 *= t1
            n1 = t1 * t1 * (self.grad3[gi1] * x1 + self.grad3[gi1 + 1] * y1 + self.grad3[gi1 + 2] * z1)

        t2 = 0.6 - x2 * x2 - y2 * y2 - z2 * z2
        if t2 < 0:
            n2 = 0.0
        else:
            gi2 = self.permMod12[ii + i2 + self.perm[jj + j2 + self.perm[kk + k2]]] * 3
            t2 *= t2
            n2 = t2 * t2 * (self.grad3[gi2] * x2 + self.grad3[gi2 + 1] * y2 + self.grad3[gi2 + 2] * z2)

        t3 = 0.6 - x3 * x3 - y3 * y3 - z3 * z3
        if t3 < 0:
            n3 = 0.0
        else:
            gi3 = self.permMod12[ii + 1 + self.perm[jj + 1 + self.perm[kk + 1]]] * 3
            t3 *= t3
            n3 = t3 * t3 * (self.grad3[gi3] * x3 + self.grad3[gi3 + 1] * y3 + self.grad3[gi3 + 2] * z3)

        # Add contributions from each corner to get the final noise value.
        # The result is scaled to stay just inside [-1, 1]
        return 32.0 * (n0 + n1 + n2 + n3)


    # 4D simplex noise, better simplex rank ordering method 2012-03-09
    def noise4d(self, x=0.0, y=0.0, z=0.0, w=0.0):
        # Noise contributions from the five corners
        n0 = 0.0
        n1 = 0.0
        n2 = 0.0
        n3 = 0.0
        n4 = 0.0
        # Skew the (x, y, z, w) space to determine which cell of 24 simplices we're in
        # Factor for 4D skewing
        s = (x + y + z + w) * self.F4
        i = math.floor(x + s)
        j = math.floor(y + s)
        k = math.floor(z + s)
        l = math.floor(w + s)
        # Factor for 4D unskewing
        t = (i + j + k + l) * self.G4
        # Unskew the cell origin back to (x, y, z, w) space
        X0 = i - t
        Y0 = j - t
        Z0 = k - t
        W0 = l - t
        # The x,y,z,w distances from the cell origin
        x0 = x - X0
        y0 = y - Y0
        z0 = z - Z0
        w0 = w - W0
        # For the 4D case, the simplex is a 4D shape I won't even try to describe.
        # To find out which of the 24 possible simplices we're in, we need to
        # determine the magnitude ordering of x0, y0, z0 and w0.
        # Six pair-wise comparisons are performed between each possible pair
        # of the four coordinates, and the results are used to rank the numbers.
        rankx = 0
        ranky = 0
        rankz = 0
        rankw = 0
        if x0 > y0:
            rankx += 1
        else:
            ranky += 1
        if x0 > z0:
            rankx += 1
        else:
            rankz += 1
        if x0 > w0:
            rankx += 1
        else:
            rankw += 1
        if y0 > z0:
            ranky += 1
        else:
            rankz += 1
        if y0 > w0:
            ranky += 1
        else:
            rankw += 1
        if z0 > w0:
            rankz += 1
        else:
            rankw += 1

        # [rankx, ranky, rankz, rankw] is a 4-vector with the numbers 0, 1, 2 and 3
        # in some order. We use a thresholding to set the coordinates in turn.
        # Rank 3 denotes the largest coordinate.
        i1 = 1 if rankx >= 3 else 0
        j1 = 1 if ranky >= 3 else 0
        k1 = 1 if rankz >= 3 else 0
        l1 = 1 if rankw >= 3 else 0
        # Rank 2 denotes the second largest coordinate.
        i2 = 1 if rankx >= 2 else 0
        j2 = 1 if ranky >= 2 else 0
        k2 = 1 if rankz >= 2 else 0
        l2 = 1 if rankw >= 2 else 0
        # Rank 1 denotes the second smallest coordinate.
        i3 = 1 if rankx >= 1 else 0
        j3 = 1 if ranky >= 1 else 0
        k3 = 1 if rankz >= 1 else 0
        l3 = 1 if rankw >= 1 else 0
        # The fifth corner has all coordinate offsets = 1, so no need to compute that.
        # Offsets for second corner in (x, y, z, w) coords
        x1 = x0 - i1 + self.G4
        y1 = y0 - j1 + self.G4
        z1 = z0 - k1 + self.G4
        w1 = w0 - l1 + self.G4
        # Offsets for third corner in (x, y, z, w) coords
        x2 = x0 - i2 + 2.0 * self.G4
        y2 = y0 - j2 + 2.0 * self.G4
        z2 = z0 - k2 + 2.0 * self.G4
        w2 = w0 - l2 + 2.0 * self.G4
        # Offsets for fourth corner in (x, y, z, w) coords
        x3 = x0 - i3 + 3.0 * self.G4
        y3 = y0 - j3 + 3.0 * self.G4
        z3 = z0 - k3 + 3.0 * self.G4
        w3 = w0 - l3 + 3.0 * self.G4
        # Offsets for last corner in (x, y, z, w) coords
        x4 = x0 - 1.0 + 4.0 * self.G4
        y4 = y0 - 1.0 + 4.0 * self.G4
        z4 = z0 - 1.0 + 4.0 * self.G4
        w4 = w0 - 1.0 + 4.0 * self.G4
        # Work out the hashed gradient indices of the five simplex corners
        ii = int(i) & 255
        jj = int(j) & 255
        kk = int(k) & 255
        ll = int(l) & 255

        # Calculate the contribution from the five corners
        t0 = 0.6 - x0 * x0 - y0 * y0 - z0 * z0 - w0 * w0
        if t0 < 0:
            n0 = 0.0
        else:
            gi0 = (self.perm[ii + self.perm[jj + self.perm[kk + self.perm[ll]]]] % 32) * 4
            t0 *= t0
            n0 = t0 * t0 * (self.grad4[gi0] * x0 + self.grad4[gi0 + 1] * y0 + self.grad4[gi0 + 2] * z0 + self.grad4[gi0 + 3] * w0)

        t1 = float(0.6 - x1 * x1 - y1 * y1 - z1 * z1 - w1 * w1)
        if t1 < 0:
            n1 = 0.0
        else:
            gi1 = (self.perm[ii + i1 + self.perm[jj + j1 + self.perm[kk + k1 + self.perm[ll + l1]]]] % 32) * 4
            t1 *= t1
            n1 = t1 * t1 * (self.grad4[gi1] * x1 + self.grad4[gi1 + 1] * y1 + self.grad4[gi1 + 2] * z1 + self.grad4[gi1 + 3] * w1)

        t2 = float(0.6 - x2*x2 - y2*y2 - z2*z2 - w2*w2)
        if t2 < 0:
            n2 = 0.0
        else:
            gi2 = (self.perm[ii + i2 + self.perm[jj + j2 + self.perm[kk + k2 + self.perm[ll + l2]]]] % 32) * 4
            t2 *= t2
            n2 = t2 * t2 * (self.grad4[gi2] * x2 + self.grad4[gi2 + 1] * y2 + self.grad4[gi2 + 2] * z2 + self.grad4[gi2 + 3] * w2)

        t3 = 0.6 - x3*x3 - y3*y3 - z3*z3 - w3*w3
        if t3 < 0:
            n3 = 0.0
        else:
            gi3 = (self.perm[ii + i3 + self.perm[jj + j3 + self.perm[kk + k3 + self.perm[ll + l3]]]] % 32) * 4
            t3 *= t3
            n3 = t3 * t3 * (self.grad4[gi3] * x3 + self.grad4[gi3 + 1] * y3 + self.grad4[gi3 + 2] * z3 + self.grad4[gi3 + 3] * w3)

        t4 = float(0.6 - x4 * x4 - y4 * y4 - z4 * z4 - w4 * w4)
        if t4 < 0:
            n4 = 0.0
        else:
            gi4 = (self.perm[ii + 1 + self.perm[jj + 1 + self.perm[kk + 1 + self.perm[ll + 1]]]] % 32) * 4
            t4 *= t4
            n4 = t4 * t4 * (self.grad4[gi4] * x4 + self.grad4[gi4 + 1] * y4 + self.grad4[gi4 + 2] * z4 + self.grad4[gi4 + 3] * w4)

        # Sum up and scale the result to cover the range [-1, 1]
        return 27.0 * (n0 + n1 + n2 + n3 + n4)




cls = SimplexNoiseClass()
res = cls.noise2d(1, 1)
print(res)


'''
{
    $factor1 = null1.factor1;
    $width = null1.width;
    $factorPi = null1.factorPi;
    $factorTotal = null1.factorTotal;
    $height = null1.height;
    $scalePi = null1.scalePi;
    $scale1 = null1.scale1;


    $e = 2.718281828459045;
    $pi = 3.141592653589793;
    null1.ty = $factorTotal * ($factor1 * sin($scale1 * time) - $width * sin($height * $e * time) + $factorPi * sin($scalePi * $pi * time));
}
'''
