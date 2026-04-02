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

for i in range(num_subchaves):
    subchave_nome = winreg.EnumKey(chave_aberta, i)
    print(subchave_nome)

    # Abrimos a subchave para ler os valores
    subchave_aberta = winreg.OpenKey(chave_aberta, subchave_nome)

    try:
        display_name, _ = winreg.QueryValueEx(subchave_aberta, "DisplayName")
        print(f"Nome do programa: {display_name}")
    except FileNotFoundError:
        print(f"error {i}")
        pass  # A chave DisplayName pode não existir

    winreg.CloseKey(subchave_aberta)