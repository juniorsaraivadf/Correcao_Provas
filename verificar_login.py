import getpass
from pathlib import Path
import tomllib

from auth import verify_password


def main() -> None:
  caminho_secrets = Path(".streamlit/secrets.toml")
  try:
    config = tomllib.loads(caminho_secrets.read_text(encoding="utf-8"))
  except FileNotFoundError:
    print("Arquivo .streamlit/secrets.toml não encontrado nesta pasta.")
    return
  except tomllib.TOMLDecodeError as error:
    print(f"Não foi possível ler o secrets.toml: {error}")
    return

  auth = config.get("auth", {})
  users = auth.get("users", {}) if isinstance(auth, dict) else {}
  if not isinstance(users, dict) or not users:
    print("Nenhum usuário está configurado em [auth.users].")
    return

  print("Usuários configurados:", ", ".join(sorted(users)))
  username = input("Digite o usuário exatamente como aparece acima: ").strip()
  password = getpass.getpass("Digite a senha: ")
  password_hash = users.get(username)

  if isinstance(password_hash, str) and verify_password(password, password_hash):
    print("Resultado: usuário e senha correspondem.")
  else:
    print("Resultado: usuário e senha não correspondem à configuração local.")


if __name__ == "__main__":
  main()
