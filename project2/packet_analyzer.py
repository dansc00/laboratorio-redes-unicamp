from scapy.all import *
import numpy as np

# analisador de pacotes em capturas .pcap
class PacketAnalyzer:

    def __init__(self, packets=None):
        self.packets = packets

    # mensagens de falha
    def icmpFail(self):
        print("The packet doesn't have an ICMP layer")
        return None

    def ipFail(self):
        print("The packet doesn't have an IP layer")
        return None
    
    # métodos gerais
    # retorna pacotes
    def getPackets(self):
        return self.packets
    
    # retorna número total de pacotes
    def getTotalPackets(self):
        return len(self.getPackets())
    
    # retorna total de bytes somados nos pacotes 
    def getTotalBytes(self):
        return sum(len(pkt) for pkt in self.packets) if self.getTotalPackets() > 0 else 0
    
    # retorna tempo total de captura
    def getTotalTime(self):

        if self.getTotalPackets() <= 0:
            print("The capture doesn't have any packets")
            return 0

        startTime = float(self.getPackets()[0].time)
        endTime = float(self.getPackets()[-1].time)

        return endTime - startTime
    
    # recebe dois pacotes e retorna a diferença de tempo entre eles
    def getTimeDiff(self, pkt1, pkt2):
        return float(pkt2.time - pkt1.time)
    
    # retorna estatísticas de jitter: lista de jitters medidos e média
    def getJitterStats(self, intervals):

        if self.getTotalPackets() < 3:
            print("There is no way to measure jitter with less than three packets")
            return 0
        
        jitters = np.diff(intervals) if len(intervals) > 0 else []
        mean = np.mean(jitters) if len(jitters) > 0 else 0
        std = np.std(jitters) if len(jitters) > 0 else 0

        return {"jitters": jitters,
                "mean": mean,
                "std": std}

    # retorna throughput medido em bps
    def getThroughput(self):

        totalTime = self.getTotalTime()
        totalBytes = self.getTotalBytes()
        totalBits = totalBytes * 8

        return totalBits/totalTime if totalTime > 0 else 0

    # métodos para análise IP
    # retorna IP de origem 
    def getSrcIp(self, pkt):
        return pkt[IP].src if IP in pkt else self.ipFail()

    # retorna IP de destino
    def getDstIp(self, pkt):
        return pkt[IP].dst if IP in pkt else self.ipFail()
    
    # métodos para análise ICMP
    # retorna número de sequência de pacote ICMP
    def getIcmpSeq(self, pkt):
        return pkt[ICMP].seq if ICMP in pkt else self.icmpFail()
    
    # retorna tipo de ICMP: 0 = echo request , 8 = echo reply
    def getIcmpType(self, pkt):
        return pkt[ICMP].type if ICMP in pkt else self.icmpFail()

    # retorna lista de sequência de pacotes ICMP em ordem crescente (sem duplicatas)
    def getIcmpSeqsList(self):

        seqsList = set() # conjunto sem duplicatas
        for pkt in self.getPackets():
            if ICMP in pkt:
                seqsList.add(self.getIcmpSeq(pkt))

        return sorted(list(seqsList)) if seqsList else []

    # retorna estatísticas de RTT ICMP: lista de RTT, média, máximo, mínimo e desvio padrão
    def getIcmpRttStats(self):

        rtts = []
        requests = {}

        for pkt in self.getPackets():
            if ICMP in pkt:
                seq = self.getIcmpSeq(pkt)

                if self.getIcmpType(pkt) == 8: # echo request
                    requests[seq] = pkt

                elif self.getIcmpType(pkt) == 0 and seq in requests: # echo reply
                    rtts.append(self.getTimeDiff(requests[seq], pkt))

        rtts = np.array(rtts) if rtts else []
        mean = np.mean(rtts) if len(rtts) > 0 else 0 
        max = np.max(rtts) if len(rtts) > 0 else 0
        min = np.min(rtts) if len(rtts) > 0 else 0
        std = np.std(rtts) if len(rtts) > 0 else 0

        return {"rtts": rtts,
                "mean": mean,
                "max": max,
                "min": min,
                "std": std}
    
    # retorna estatísticas de intervalo de chegada entre pacotes ICMP consecutivos: lista de intervalos, média e desvio padrão
    def getIcmpIntervalStats(self):

        if self.getTotalPackets() < 2:
            print("There is no way to measure interval with less than two packets")
            return None

        requestTimes = []

        for pkt in self.getPackets():
            if ICMP in pkt:
                if self.getIcmpType(pkt) == 8:
                    requestTimes.append(float(pkt.time))

        intervals = np.diff(requestTimes) if requestTimes else []  # diferença entre tempos consecutivos
        mean = np.mean(intervals) if len(intervals) > 0 else 0
        std = np.std(intervals) if len(intervals) > 0 else 0

        return {"intervals": intervals,
                "mean": mean,
                "std": std} 
    
    # retorna estatísticas de perda de pacotes: enviados, recebidos, perdidos, taxa de percas
    def getIcmpPacketLossStats(self):

        sent = 0
        seqReceived = set()

        for pkt in self.getPackets():
            if ICMP in pkt:
                if self.getIcmpType(pkt) == 8:
                    sent += 1

                elif self.getIcmpType(pkt) == 0:
                    seqReceived.add(self.getIcmpSeq(pkt))
        
        received = len(seqReceived)
        lost = sent - received
        lossRate = (lost * 100)/sent if sent > 0 else 0

        return {"sent": sent, 
                "received": received, 
                "lost": lost, 
                "lossRate": lossRate}

    # imprime métricas ICMP
    def printIcmpMetrics(self):

        bytes = self.getTotalBytes()
        src = self.getSrcIp(self.getPackets()[0])
        dst = self.getDstIp(self.getPackets()[0])
        rttStats = self.getIcmpRttStats()
        intervalStats = self.getIcmpIntervalStats()
        jitterStats = self.getJitterStats(intervalStats["intervals"])
        throughput = self.getThroughput()
        lossStats = self.getIcmpPacketLossStats()

        print(f"Total bytes: {bytes} bytes")
        print(f"IP source: {src}")
        print(f"IP destination: {dst}")
        print(f"Mean RTT: {rttStats["mean"]*1000:.2f} ms \
                RTT standard deviation: {rttStats["std"]*1000:.2f} ms \
                Maximum RTT: {rttStats["max"]*1000:.2f} ms \
                Minimum RTT: {rttStats["min"]*1000:.2f} ms")
        print(f"Mean packet arrival time: {intervalStats["mean"]:.2f} s")
        print(f"Mean jitter: {jitterStats["mean"]*1000:.2f} ms \
                Jitter standard deviation: {jitterStats["std"]*1000:.2f} ms")
        print(f"Throughput: {throughput/1000000:.4f} Mbps")
        print(f"{lossStats["sent"]} packages sent \
                {lossStats["received"]} packages received \
                {lossStats["lost"]} packages lost \
                Loss rate = {lossStats["lossRate"]:.1f}%")
        print()
    
