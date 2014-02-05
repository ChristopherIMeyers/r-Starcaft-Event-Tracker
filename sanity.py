import unittest
class CheckSanity(unittest.TestCase):
  def test_bad(self):
    self.assertTrue(False)

if __name__ == '__main__':
  unittest.main()