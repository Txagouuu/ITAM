import asyncio
import socket
from scapy.all import ARP, Ether, srp
from pysnmp.hlapi.v3arch.asyncio import *
import urllib.request

# --- BUSCA FABRICANTE PELO MAC (Online API) ---
def get_mac_vendor(mac_address):
    try:
        url = f"https://api.macvendors.com/{mac_address}"
        # Timeout curto para não travar o script se a API demorar
        response = urllib.request.urlopen(url, timeout=1)
        return response.read().decode('utf-8')
    except:
        return "Desconhecido"

# --- BUSCA MODELO VIA SNMP ---
async def get_snmp_info(ip, community='public'):
    snmp_engine = SnmpEngine()
    try:
        # Aumentei um pouco o timeout para redes com muitos dispositivos
        transport = await UdpTransportTarget.create((ip, 161), timeout=1.5, retries=0)
        errorIndication, errorStatus, _, varBinds = await get_cmd(
            snmp_engine,
            CommunityData(community, mpModel=1),
            transport,
            ContextData(),
            ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'))
        )
        if not errorIndication and not errorStatus:
            return str(varBinds[0][1]).strip().replace('\r', '').replace('\n', ' ')
        return None
    except:
        return None
    finally:
        snmp_engine.close_dispatcher()

# --- BUSCA NOME DO DISPOSITIVO (DNS) ---
def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Sem Nome"

async def main():
    rede = "192.168.1.0/24"
    print(f"[*] Iniciando descoberta avançada em {rede}...")
    
    # ARP Scan
    arp_request = ARP(pdst=rede)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    ans, _ = srp(broadcast/arp_request, timeout=2, verbose=False)
    
    print(f"\n{'IP':<15} | {'Fabricante (MAC)':<20} | {'Identificação (SNMP/Host)'}")
    print("-" * 85)
    
    for _, rcved in ans:
        ip = rcved.psrc
        mac = rcved.hwsrc
        
        # 1. Tenta Fabricante
        vendor = get_mac_vendor(mac)
        
        # 2. Tenta SNMP (Modelo Real)
        snmp_data = await get_snmp_info(ip)
        
        # 3. Tenta Hostname (Nome na rede)
        hostname = get_hostname(ip)
        
        # Lógica de exibição: prioriza SNMP, depois Hostname
        info_final = snmp_data if snmp_data else hostname
        
        print(f"{ip:<15} | {vendor[:20]:<20} | {info_final[:45]}")
        
        # Delay para respeitar o limite da API de MAC Vendors
        await asyncio.sleep(0.7)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Varredura interrompida.")