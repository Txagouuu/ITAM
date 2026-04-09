import asyncio
import ipaddress
from pysnmp.hlapi.v3arch.asyncio import *

async def get_device_info(target_ip, community='public'):
    oid = '1.3.6.1.2.1.1.1.0'
    snmp_engine = SnmpEngine()
    
    try:
        # Timeout curto (0.5s) para a varredura não demorar uma eternidade
        transport = await UdpTransportTarget.create((str(target_ip), 161), timeout=0.5, retries=0)
        
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            snmp_engine,
            CommunityData(community, mpModel=1),
            transport,
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        if not errorIndication and not errorStatus:
            for varBind in varBinds:
                return str(varBind[1])
        return None
    except:
        return None
    finally:
        snmp_engine.close_dispatcher()

async def main():
    # Define a sua rede (ajuste para a sua realidade)
    rede = ipaddress.ip_network('192.168.1.0/24')
    comunidade = 'public'
    
    print(f"Iniciando varredura na rede {rede}...")
    print(f"{'IP':<15} | {'Status':<12} | {'Modelo'}")
    print("-" * 60)

    # Criamos uma lista de tarefas para rodar em paralelo
    tasks = []
    for ip in rede.hosts():
        tasks.append(scan_ip(ip, comunidade))
    
    # Executa tudo simultaneamente (Muito mais rápido!)
    await asyncio.gather(*tasks)

async def scan_ip(ip, comunidade):
    modelo = await get_device_info(ip, comunidade)
    if modelo:
        print(f"{str(ip):<15} | ONLINE       | {modelo[:100]}...")
    # Se quiser ver os que falharam, descomente a linha abaixo:
    # else: print(f"{str(ip):<15} | OFFLINE")

if __name__ == "__main__":
    asyncio.run(main())