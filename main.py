import winreg
import cryptography

# 1. Definimos o caminho 
caminho_uninstall = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"

# 2. Abrimos a chave
# HKEY_LOCAL_MACHINE é a raiz que abriga as configurações da máquina
chave_aberta = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, caminho_uninstall)

# 3. Listamos as subchaves
num_subchaves = winreg.QueryInfoKey(chave_aberta)[0]

print(num_subchaves)