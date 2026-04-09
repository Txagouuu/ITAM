import os
import csv
import wmi
from scapy.all import ARP, Ether, srp
from dotenv import load_dotenv

# Carrega credenciais
load_dotenv()
USUARIO_PADRAO = os.getenv("AUDIT_USER")
SENHA_PADRAO = os.getenv("AUDIT_PASS")

def varrer_rede_arp(ip_range):
    """Varre a rede inteira e retorna lista de IPs ativos"""
    print(f"[*] Varrendo a rede {ip_range} via ARP...")
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    pacote = ether/arp

    # Envia o broadcast e recebe respostas
    resultado = srp(pacote, timeout=3, verbose=False)[0]
    
    ips_ativos = []
    for enviado, recebido in resultado:
        ips_ativos.append(recebido.psrc)
    
    print(f"[!] {len(ips_ativos)} dispositivos encontrados na rede.")
    return ips_ativos

def realizar_auditoria(ips, user, password):
    """Tenta conectar via WMI em cada IP encontrado"""
    resultados = []
    print(f"\n{'IP':<15} | {'Status':<12} | {'Modelo'}")
    print("-" * 60)

    for ip in ips:
        try:
            # Conexão WMI (Precisa rodar como Admin no Windows)
            conexao = wmi.WMI(ip, user=user, password=password)
            cs = conexao.Win32_ComputerSystem()[0]
            bios = conexao.Win32_Bios()[0]
            
            item = {
                "IP": ip,
                "Status": "Sucesso",
                "Nome": cs.Name,
                "Fabricante": cs.Manufacturer,
                "Modelo": cs.Model,
                "Serial": bios.SerialNumber
            }
            print(f"{ip:<15} | CONECTADO    | {item['Modelo'][:25]}")
            resultados.append(item)
            
        except Exception:
            # Se falhar (dispositivo não Windows, ou sem permissão)
            print(f"{ip:<15} | SEM ACESSO   | (Possível Celular/Router/Linux)")
            resultados.append({"IP": ip, "Status": "Sem Acesso", "Nome": "N/A", "Fabricante": "N/A", "Modelo": "N/A", "Serial": "N/A"})

    return resultados

def salvar_csv(dados):
    with open('inventario_rede_completo.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["IP", "Status", "Nome", "Fabricante", "Modelo", "Serial"])
        writer.writeheader()
        writer.writerows(dados)
    print(f"\n[!] Inventário salvo em 'inventario_rede_completo.csv'")

if __name__ == "__main__":
    # 1. Defina o range da rede (ex: 192.168.1.0/24)
    # Dica: use 'ipconfig' no terminal para confirmar sua sub-rede
    minha_rede = "192.168.1.0/24" 
    
    # 2. Executa a varredura automática
    lista_viva = varrer_rede_arp(minha_rede)
    
    # 3. Executa a auditoria nos IPs encontrados
    if lista_viva:
        relatorio = realizar_auditoria(lista_viva, USUARIO_PADRAO, SENHA_PADRAO)
        salvar_csv(relatorio)