from scapy.all import *
import numpy as np

# manipulador de captura de pacotes .pcap
class CaptureHandler:

    def __init__(self, PATH=""):
        self.cpt = rdpcap(PATH)

    # mensagens de falha
    def icmpFail():
        print("The packet doesn't have an ICMP layer")
        return None

    def ipFail():
        print("The packet doesn't have an IP layer")
        return None
    
    # métodos gerais
    # retorna número total de pacotes na captura
    def getTotalPacks(self):
        return len(self.cpt)

    # recebe pacote origem e destino, retorna o RTT medido em s(apenas retorna o valor correto se a captura partiu de um host)
    def getRtt(self, src, dst):
        return float(dst.time - src.time)
    
    # retorna RTT médio
    def getAverageRtt(self, rtts):
        return np.mean(rtts) if len(rtts) > 0 else 0
    
    # retorna maior RTT
    def getMaxRtt(self, rtts):
        return np.max(rtts) if len(rtts) > 0 else 0
    
    # retorna menor RTT
    def getMinRtt(self, rtts):
        return np.min(rtts) if len(rtts) > 0 else 0
    
    # retorna desvio padrão de RTTs
    def getRttStdDeviation(self, rtts):
        return np.std(rtts) if len(rtts) > 0 else 0

    # retorna throughput medido em bps
    def getThroughput(self):

        startTime = float(self.cpt[0].time)
        endTime = float(self.cpt[-1].time)
        duration = endTime - startTime

        totalBytes = sum(len(pkt) for pkt in self.cpt)
        totalBits = totalBytes * 8

        return totalBits/duration

    # métodos IP
    # retorna IP de origem encontrado na camada IP
    def getSrcIp(self, pkt):
        return pkt[IP].src if IP in pkt else self.ipFail()

    # retorna IP de destino encontrado na camada IP
    def getDstIp(self, pkt):
        return pkt[IP].dst if IP in pkt else self.ipFail()
    
    # métodos ICMP
    # retorna número de sequência de pacote ICMP
    def getIcmpSeq(self, pkt):
        return pkt[ICMP].seq if ICMP in pkt else self.icmpFail()

    # retorna lista de sequência de pacotes ICMP em ordem crescente (sem duplicatas)
    def getIcmpSeqsList(self):

        seqsList = set()
        for pkt in self.cpt:
            if ICMP in pkt:
                seqsList.add(self.getIcmpSeq(pkt))
            else:
                self.icmpFail()

        return sorted(list(seqsList))

    # retorna lista de RTTs medidos entre requisições e respostas ICMP (apenas retorna o valor correto se a captura partiu de um host)
    def getIcmpRttList(self):

        rttList = []
        requests = {}

        for pkt in self.cpt:
            if ICMP in pkt:
                seq = self.getIcmpSeq(pkt)

                if pkt[ICMP].type == 8: # echo request
                    requests[seq] = pkt

                elif pkt[ICMP].type == 0 and seq in requests: # echo reply
                    rttList.append(self.getRtt(requests[seq], pkt))
            else:
                self.icmpFail()

        return np.array(rttList) 
    
if __name__ == "__main__":

    # imprime métricas obtidas na análise da captura
    def printOutput(cpt):

        print(f"Total de pacotes capturados: {cpt.getTotalPacks()}")
        print(f"IP origem das requisições: {cpt.getSrcIp(cpt.cpt[0])}")
        print(f"IP destino das requisições: {cpt.getDstIp(cpt.cpt[0])}")
        print(f"RTT médio: {cpt.getAverageRtt(cpt.getIcmpRttList())*1000:.2f} ms")
        print(f"Desvio padrão de RTTs: {cpt.getRttStdDeviation(cpt.getIcmpRttList())*1000:.2f} ms")
        print(f"RTT máximo: {cpt.getMaxRtt(cpt.getIcmpRttList())*1000:.2f} ms")
        print(f"RTT mínimo: {cpt.getMinRtt(cpt.getIcmpRttList())*1000:.2f} ms")
        print(f"Throughput: {cpt.getThroughput()/1000000:.4f} Mbps")
        print()

    PATH1 = "capture/h1-h3.pcap"
    PATH2 = "capture/h2-h4.pcap"
    capture1 = CaptureHandler(PATH1)
    capture2 = CaptureHandler(PATH2)

    printOutput(capture1)
    printOutput(capture2)

    
