import unittest

from auth import hash_password, verify_password


class PasswordHashTests(unittest.TestCase):
  def test_hash_verifies_matching_password(self):
    password = "senha-de-teste-segura"
    password_hash = hash_password(password, iterations=100_000)

    self.assertTrue(verify_password(password, password_hash))
    self.assertFalse(verify_password("outra-senha-segura", password_hash))

  def test_rejects_short_password(self):
    with self.assertRaises(ValueError):
      hash_password("curta", iterations=100_000)

  def test_rejects_malformed_hash(self):
    self.assertFalse(verify_password("senha-de-teste-segura", "invalido"))


if __name__ == "__main__":
  unittest.main()
