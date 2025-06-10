import pandas as pd
from scapy.all import PcapReader

# leitura PCAP e extração dos campos
records = [] # lista de dicionarios com registros de pacotes
packets = PcapReader("200701011800.dump")

for pkt in packets:
    ts = pkt.time # timestamp
    length = len(pkt) # tamanho do pacote em bytes
    protoNum = pkt["IP"].proto if pkt.haslayer("IP") else None # número do protocolo

    # mapeia número de protocolo para nome
    protoMap = {6: "TCP", 17: "UDP", 1: "ICMP"}
    protoName = protoMap.get(protoNum, str(protoNum) if protoNum is not None else None) # nome do protocolo

    records.append({
        "timestamp": ts,
        "size": length,
        "type": protoName,
    })

# cria DataFrame e converte timestamp
df = pd.DataFrame(records) # converte em dataframe, cada dicionario é uma linha com valores e cada chave é uma coluna
df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce') # converte string para float
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")  # converte de epoch

# filtra somente pacotes que interessam
#df = df[df["type"].isin(["TCP","UDP"])]

# grava em parquet com pyarrow
df.to_parquet("capture.parquet", engine="pyarrow", compression="snappy", index=False)

packets.close()
