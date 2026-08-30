import os
from pathlib import Path
from getpass import getpass

from pwdlib import PasswordHash
#from dotenv import load_dotenvpassword


raw_password = getpass(
    "Set the password for access to the demonstration interface: "
)

password_hash = PasswordHash.recommended()
hashed = password_hash.hash(raw_password)

backend_dir = Path("backend")
env_path = backend_dir / ".env"


env_path.write_text(
    f'APP_PASSWORD_HASH="{hashed}"\n',
    encoding="utf-8"
)

print("Password has been configured.")
