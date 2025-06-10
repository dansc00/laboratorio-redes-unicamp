from scapy.all import IP
import numpy as np
from analyzer.packet_analyzer import PacketAnalyzer

# analisador de camada IPv4
class IpAnalyzer(PacketAnalyzer):

    def __init__(self, id=None, path=None):
        super().__init__(id, path)
    
    # retorna IPv4 de origem
    @staticmethod
    def getSrcIp(pkt):
        if IP in pkt:
            return pkt[IP].src
        
        else:
            print("The packet doesn't have an IP layer")
            return None

    # retorna IPv4 de destino
    @staticmethod
    def getDstIp(pkt):
        if IP in pkt:
            return pkt[IP].dst
        
        else:
            print("The packet doesn't have an IP layer")
            return None