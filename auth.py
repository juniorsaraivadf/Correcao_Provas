import base64
import binascii
import getpass
import hashlib
import hmac
import secrets
import sys

ALGORITHM = "pbkdf2_sha256"
DEFAULT_ITERATIONS = 600_000
MIN_PASSWORD_LENGTH = 12


def hash_password(password: str, iterations: int = DEFAULT_ITERATIONS) -> str:
  if len(password) < MIN_PASSWORD_LENGTH:
    raise ValueError(
        f"A senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres."
    )
  if not 100_000 <= iterations <= 2_000_000:
    raise ValueError("O número de iterações está fora do intervalo permitido.")

  salt = secrets.token_bytes(16)
  digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
  salt_encoded = base64.urlsafe_b64encode(salt).decode("ascii").rstrip("=")
  digest_encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
  return f"{ALGORITHM}${iterations}${salt_encoded}${digest_encoded}"


def verify_password(password: str, encoded_hash: str) -> bool:
  try:
    algorithm, iterations_text, salt_encoded, expected_encoded = (
        encoded_hash.split("$")
    )
    iterations = int(iterations_text)
    if algorithm != ALGORITHM or not 100_000 <= iterations <= 2_000_000:
      return False

    salt = base64.b64decode(
        salt_encoded + "=" * (-len(salt_encoded) % 4),
        altchars=b"-_",
        validate=True,
    )
    expected = base64.b64decode(
        expected_encoded + "=" * (-len(expected_encoded) % 4),
        altchars=b"-_",
        validate=True,
    )
    if len(salt) != 16 or len(expected) != 32:
      return False
    actual = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(actual, expected)
  except (AttributeError, binascii.Error, TypeError, ValueError):
    return False


def main() -> None:
  print("Gerador de hash de senha para o arquivo secrets.toml.")
  password = getpass.getpass("Nova senha (mínimo 12 caracteres): ")
  confirmation = getpass.getpass("Confirme a senha: ")
  if password != confirmation:
    sys.exit("As senhas não conferem.")
  try:
    print("\nHash para copiar na configuração:")
    print(hash_password(password))
  except ValueError as error:
    sys.exit(str(error))


if __name__ == "__main__":
  main()
