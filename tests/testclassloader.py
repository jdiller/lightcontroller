import unittest
from lightcontroller.classloader import ClassLoader

class TestClassLoder(unittest.TestCase):
    def test_can_create(self):
        cl = ClassLoader()
        self.assertIsNotNone(cl)


