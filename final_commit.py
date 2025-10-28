#!/usr/bin/env python
import subprocess

subprocess.run(['git', 'add', '-A'])
subprocess.run(['git', 'commit', '-m', 'Adicionar documentação sobre signals do Facebook'])
subprocess.run(['git', 'push', 'origin', 'main'])

print("✅ Enviado!")

