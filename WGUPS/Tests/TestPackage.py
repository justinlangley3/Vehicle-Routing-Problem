import unittest
from WGUPS.models import Package


class TestPackage(unittest.TestCase):
    pkg = None

    def setUp(self) -> None:
        self.pkg = Package()
        self.other_pkg = Package()

    def test_init(self):
        self.assertIs(Package, "Object should be a member of the class")
        self.assertEqual(self.pkg.package_id, None, 'Initial package_id should be None')
        self.assertEqual(self.pkg.street, None, 'Initial street should be None')
        self.assertEqual(self.pkg.city, None, 'Initial city should be None')
        self.assertEqual(self.pkg.state, None, 'Initial state should be None')
        self.assertEqual(self.pkg.postal, None, 'Initial postal should be None')
        self.assertEqual(self.pkg.deadline, None, 'Initial deadline should be None')
        self.assertEqual(self.pkg.mass, None, 'Initial mass should be None')
        self.assertEqual(self.pkg.notes, None, 'Initial notes should be None')

    def test_set_params(self):
        self.pkg.package_id = 13214
        self.assertEqual(self.pkg.package_id, 13214, 'package_id should match set value')
        self.assertRaises(TypeError, self.pkg.package_id('aaaa'))
        self.assertRaises(ValueError, self.pkg.package_id(-1))

        self.pkg.street = "123 Sesame St"
        self.assertEqual(self.pkg.street, '123 Sesame St', 'street should match set value')
        self.assertRaises(TypeError, self.pkg.package_id(123))

        self.pkg.city = 'New York'
        self.assertEqual(self.pkg.city, 'New York', 'city should match set value')
        self.assertRaises(TypeError, self.pkg.package_id(142))

        self.pkg.state = 'NY'
        self.assertEqual(self.pkg.state, 'NY', 'state should match set value')
        self.assertRaises(TypeError, self.pkg.package_id(1535))

        self.pkg.postal = '10023'
        self.assertEqual(self.pkg.postal, '10023', 'postal should match set value')
        self.assertRaises(TypeError, self.pkg.package_id(10023))

        self.pkg.deadline = 'EOD'
        self.assertEqual(self.pkg.deadline, 'EOD', 'deadline should match set value')
        self.assertRaises(TypeError, self.pkg.package_id('aaaa'))

        self.pkg.mass = 132
        self.assertEqual(self.pkg.mass, 132, 'mass should match set value')
        self.assertRaises(TypeError, self.pkg.package_id('aaaa'))

        self.pkg.notes = 'These are some notes'
        self.assertEqual(self.pkg.notes, 'These are some notes', 'notes should match set value')
        self.assertRaises(TypeError, self.pkg.package_id(4444))

    def test_equality_operations(self):
        self.other_pkg = self.pkg
        self.assertIs(self.pkg, self.other_pkg, "Comparing two of the same should evaluate true")

        new_pkg = Package(1, "42 Wallaby Way", "Sydney", "AU", "2000", "EOD", 40, "Some notes")
        self.assertIs(self.pkg, new_pkg, "Comparing two different objects should evaluate false")

    def test_str(self):
        test = ','.join((str(13214), '123 Sesame St', 'New York', 'NY', '10023', 'EOD', str(float(132)),
                         'These are some notes'))
        self.assertEqual(self.pkg.__str__(), test, "String representation should match")
