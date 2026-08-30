# sets the instruction to show at the website

import os
from pathlib import Path

backend_dir = Path("backend")#
write_path = backend_dir / 'instruction.txt'

instruction = str(input('Input the instruction you want to display at the web-page for the users of your model:'))
print(instruction)

with open (write_path, 'w', encoding="utf-8") as f:
    f.write(instruction)

print("Instruction has been configured.")