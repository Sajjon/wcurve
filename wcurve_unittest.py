"""
Author: Sebastien Martini (seb@dbzteam.org)
License: MIT
"""
import unittest
import copy
import random
# Local imports
import wcurve

class TestWCurveArithmetic(unittest.TestCase):
    def setUp(self):
        self.curve = wcurve.secp256r1_curve()

    def testEq(self):
        self.assertEqual(self.curve.base_point, self.curve.base_point)
        self.assertEqual(self.curve.point_at_infinity, self.curve.point_at_infinity)
        self.assertEqual(self.curve.point_at_infinity, -self.curve.point_at_infinity)
        inf = copy.copy(self.curve.point_at_infinity)
        inf._multiple(10)
        self.assertEqual(self.curve.point_at_infinity, inf)
        self.assertFalse(self.curve.base_point == self.curve.point_at_infinity)
        self.assertTrue(self.curve.base_point != self.curve.point_at_infinity)

    def testSub(self):
        r = self.curve.base_point - self.curve.base_point
        self.assertEqual(r, self.curve.point_at_infinity)
        r = self.curve.point_at_infinity - self.curve.point_at_infinity
        self.assertEqual(r, self.curve.point_at_infinity)
        r = self.curve.base_point - self.curve.point_at_infinity
        self.assertEqual(r, self.curve.base_point)
        r = self.curve.point_at_infinity - self.curve.base_point
        self.assertEqual(r, -self.curve.base_point)

    def testAdd(self):
        r = self.curve.base_point + self.curve.point_at_infinity
        self.assertEqual(r, self.curve.base_point)
        r = self.curve.base_point + (2 * self.curve.base_point)
        self.assertEqual(r, (3 * self.curve.base_point))
        r = self.curve.base_point + self.curve.base_point
        self.assertEqual(r, 2 * self.curve.base_point)
        r = self.curve.point_at_infinity + self.curve.point_at_infinity
        self.assertEqual(r, self.curve.point_at_infinity)
        s1 = random.SystemRandom().randint(1, self.curve.n - 1)
        s2 = random.SystemRandom().randint(1, self.curve.n - 1)
        r = s1 * self.curve.base_point + s2 * self.curve.base_point
        self.assertEqual(r, (s1 + s2) * self.curve.base_point)

    def testMul(self):
        r = self.curve.n * self.curve.base_point
        self.assertEqual(r, self.curve.point_at_infinity)
        r = 1 * self.curve.base_point
        self.assertEqual(r, self.curve.base_point)
        s = random.SystemRandom().randint(1, self.curve.n - 1)
        r = s * self.curve.base_point
        r = r.to_affine()
        r = wcurve.JacobianPoint(r[0], r[1], 1, self.curve)
        r = self.curve.n * r
        self.assertEqual(r, self.curve.point_at_infinity)
        self.assertRaises(ValueError,
                          lambda: 2 * self.curve.point_at_infinity)
        b = copy.copy(self.curve.base_point)
        b.x += 1
        self.assertRaises(ValueError, lambda: 2 * b)
        r = 0 * self.curve.base_point
        self.assertEqual(r, self.curve.point_at_infinity)
        r1 = -42 * self.curve.base_point
        r2 = ((-42) % self.curve.n) * self.curve.base_point
        self.assertEqual(r1, r2)

    def testMulRef(self):
        # (x, y) = s * base_point obtained with openssl
        s = 55410786546881778422887285187544511127100960212956419513245461364050667784185
        x = 64169503900361343289983195807258161414745802527383776807124463141740561324790
        y = 111970075840193383282111507227885172446728586957098158699813435561710172438460
        ref = wcurve.JacobianPoint(x, y, 1, self.curve)
        r = s * self.curve.base_point
        self.assertEqual(r, ref)

    def testCompression(self):
        bit_y = self.curve.base_point.compression_bit_y()
        p = wcurve.JacobianPoint.uncompress(self.curve.base_point.x, bit_y, self.curve)
        self.assertEqual(p, self.curve.base_point)
        p = wcurve.JacobianPoint.uncompress(self.curve.base_point.x, 1 - bit_y, self.curve)
        self.assertEqual(p, -self.curve.base_point)

class TestVerifiedScalarMul(unittest.TestCase):
    def setUp(self):
        self.curve = wcurve.secp256r1_curve_with_correctness_check()

    def testMul(self):
        sk = random.SystemRandom().randint(1, self.curve.n - 1)
        pk1 = self.curve.base_point.scalar_multiplication(sk)
        pk2 = self.curve.base_point.verified_scalar_multiplication(sk)
        self.assertEqual(pk1, pk2)

if __name__ == '__main__':
    unittest.main()
