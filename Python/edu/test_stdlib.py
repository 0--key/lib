import unittest


class TestGeneric(unittest.TestCase):

    def test_true(self):
        self.assertTrue(1 + 3 == 4)

    def test_false(self):
        self.assertFalse(1 + 4 == 4)

    def test_none(self):
        value = None
        self.assertIsNone(value)

    # def test_not_implemented(self):
    #     self.assertTrue("abc" < 123)

    # def test_ellipsis(self):
    #     self.assertTrue('ellipsis' == type(Ellipsis))

    # def test__debug__(self):
    #     self.assertTrue(__debug__)
