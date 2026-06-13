import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import PortScanner, COMMON_PORTS


class TestPortScanner(unittest.TestCase):
    def test_common_ports(self):
        self.assertEqual(COMMON_PORTS[22], "SSH")
        self.assertEqual(COMMON_PORTS[80], "HTTP")
        self.assertEqual(COMMON_PORTS[443], "HTTPS")

    def test_parse_ports_range(self):
        scanner = PortScanner()
        ports = scanner.parse_ports("1-10")
        self.assertEqual(ports, list(range(1, 11)))

    def test_parse_ports_list(self):
        scanner = PortScanner()
        ports = scanner.parse_ports("80,443,8080")
        self.assertEqual(ports, [80, 443, 8080])

    def test_parse_ports_mixed(self):
        scanner = PortScanner()
        ports = scanner.parse_ports("1-5,80,443")
        self.assertEqual(ports, [1, 2, 3, 4, 5, 80, 443])


if __name__ == '__main__':
    unittest.main()
