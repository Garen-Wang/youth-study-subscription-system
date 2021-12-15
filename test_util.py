from unittest import TestCase

from util import convert


class Test(TestCase):
    def test_zero(self):
        assert convert('零') == 0

    def test_one(self):
        assert convert('一') == 1

    def test_eight(self):
        assert convert('八') == 8

    def test_ten(self):
        assert convert('十') == 10

    def test_eleven(self):
        assert convert('十一') == 11

    def test_twenty(self):
        assert convert('二十') == 20

    def test_twenty_one(self):
        assert convert('二十一') == 21

    def test_thirty(self):
        assert convert('三十') == 30

    def test_one_hundred(self):
        assert convert('一百') == 100

