from scapy.all import *
import numpy as np
from packet_analyzer import PacketAnalyzer
from ip_analyzer import IpAnalyzer

# analisador de camada ICMP
class IcmpAnalyzer(PacketAnalyzer):

    def __init__(self, id=None, packetsMargin=None, path=None):
        super().__init__(id, packetsMargin, path)
    
    # retorna número de sequência de pacote ICMP
    def getIcmpSeq(self, pkt):

        if ICMP in pkt:
            return pkt[ICMP].seq
        
        else:
            print("The packet doesn't have an ICMP layer")
            return 0
    
    # retorna tipo de ICMP: 0 = echo request , 8 = echo reply
    def getIcmpType(self, pkt):
        
        if ICMP in pkt:
            return pkt[ICMP].type
        
        else:
            print("The packet doesn't have an ICMP layer")
            return 0

    # retorna lista de sequência de pacotes ICMP em ordem crescente (sem duplicatas)
    def getIcmpSeqsList(self):

        seqsList = set() # conjunto sem duplicatas
        for pkt in self.getPackets():
            if ICMP in pkt:
                seqsList.add(self.getIcmpSeq(pkt))

        return sorted(list(seqsList)) if seqsList else []

    # retorna estatísticas de rtt ICMP: lista de rtt, desvio padrão, média, máximo, mínimo, erro padrão e coeficiente de variação
    # override
    def getRttStats(self):

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
        std = np.std(rtts) if len(rtts) > 0 else 0
        max = np.max(rtts) if len(rtts) > 0 else 0
        min = np.min(rtts) if len(rtts) > 0 else 0
        error = std/np.sqrt(len(rtts)) if len(rtts) > 0 else 0
        cv = (std/mean)*100 if mean > 0 else 0

        return {"rtts": rtts,
                "mean": mean,
                "std": std,
                "max": max,
                "min": min,
                "error": error,
                "cv": cv
                }
    
    # retorna estatísticas de intervalo de chegada entre requisições ICMP: lista de intervalos, média, desvio padrão, máximo, mínimo, erro padrão e coeficiente de variação
    # override
    def getIntervalStats(self):

        if self.getTotalPackets() < 2:
            print("There is no way to measure interval with less than two packets")
            return None

        requestTimes = []

        for pkt in self.getPackets():
            if ICMP in pkt:
                if self.getIcmpType(pkt) == 8:
                    requestTimes.append(self.getTime(pkt))

        intervals = np.diff(requestTimes) if requestTimes else []  # diferença entre tempos consecutivos
        mean = np.mean(intervals) if len(intervals) > 0 else 0
        std = np.std(intervals) if len(intervals) > 0 else 0
        max = np.max(intervals) if len(intervals) > 0 else 0
        min = np.min(intervals) if len(intervals) > 0 else 0
        error = std/np.sqrt(len(intervals)) if len(intervals) > 0 else 0
        cv = (std/mean)*100 if mean > 0 else 0

        return {"intervals": intervals,
                "mean": mean,
                "std": std,
                "max": max,
                "min": min,
                "error": error,
                "cv": cv
                } 

    # retorna estatísticas de perda de pacotes: enviados, recebidos, perdidos, taxa de perdas
    # override
    def getLossStats(self):

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
        lossStats = [sent, received, lost]

        return {"sent": sent, 
                "received": received, 
                "lost": lost, 
                "lossRate": lossRate,
                "lossStats": lossStats
                }

    # imprime métricas ICMP
    # override
    def printGeneralMetrics(self):

        id = self.getId()
        src = IpAnalyzer.getSrcIp(self.getPacket(0))
        dst = IpAnalyzer.getDstIp(self.getPacket(0))
        totalPackets = self.getTotalPackets()
        totalBytes = self.getTotalBytes()
        layers = self.getLayers().get("layers")
        throughput = self.getThroughput()

        return super().printGeneralMetrics(id, src, dst, totalPackets, totalBytes, layers, throughput)

    # override
    def printRttMetrics(self):

        layer = "ICMP"
        mean = self.getRttStats().get("mean")
        std = self.getRttStats().get("std")
        max = self.getRttStats().get("max")
        min = self.getRttStats().get("min")
        error = self.getRttStats().get("error")
        cv = self.getRttStats().get("cv")

        return super().printRttMetrics(layer, mean, std, max, min, error, cv)
    
    # override
    def printIntervalMetrics(self):

        layer = "ICMP"
        mean = self.getIntervalStats().get("mean")
        std = self.getIntervalStats().get("std")
        max = self.getIntervalStats().get("max")
        min = self.getIntervalStats().get("min")
        error = self.getIntervalStats().get("error")
        cv = self.getIntervalStats().get("cv")

        return super().printIntervalMetrics(layer, mean, std, max, min, error, cv)
    
    # override
    def printRttJitterMetrics(self):

        layer = "ICMP"
        rtts = self.getRttStats().get("rtts")
        mean = self.getJitterStats(rtts).get("mean")
        std = self.getJitterStats(rtts).get("std")
        max = self.getJitterStats(rtts).get("max")
        min = self.getJitterStats(rtts).get("min")
        error = self.getJitterStats(rtts).get("error")
        cv = self.getJitterStats(rtts).get("cv")

        return super().printRttJitterMetrics(layer, mean, std, max, min, error, cv)
    
    # override
    def printIntervalJitterMetrics(self):

        layer = "ICMP"
        intervals = self.getIntervalStats().get("intervals")
        mean = self.getJitterStats(intervals).get("mean")
        std = self.getJitterStats(intervals).get("std")
        max = self.getJitterStats(intervals).get("max")
        min = self.getJitterStats(intervals).get("min")
        error = self.getJitterStats(intervals).get("error")
        cv = self.getJitterStats(intervals).get("cv")

        return super().printIntervalJitterMetrics(layer, mean, std, max, min, error, cv)
    
    # override
    def printLossMetrics(self):

        layer = "ICMP"
        sent = self.getLossStats().get("sent")
        received = self.getLossStats().get("received")
        lost = self.getLossStats().get("lost")
        lossRate = self.getLossStats().get("lossRate")

        return super().printLossMetrics(layer, sent, received, lost, lossRate)
    
    # plotagem de gráficos ICMP
    # override
    def plotLayersGraph(self, path):

        id = self.getId()
        layers = self.getLayers().get("layers")
        nLayers = self.getLayers().get("nLayers")
        title = None
        xLabel = "Protocol layers"
        yLabel = "Amount of packets"

        return super().plotLayersGraph(path, id, layers, nLayers, title, xLabel, yLabel)

    # override
    def plotRttGraph(self, path):

        id = self.getId()
        xAxis = self.getIcmpSeqsList()
        rtts = self.getRttStats().get("rtts")
        title = None
        xLabel = "ICMP sequence number"
        yLabel = "Time (ms)"

        return super().plotRttGraph(path, id, xAxis, rtts, title, xLabel, yLabel)
    
    # override
    def plotIntervalGraph(self, path):

        id = self.getId()
        xAxis = self.getIcmpSeqsList()
        intervals = self.getIntervalStats().get("intervals")
        title = None
        xLabel = "ICMP sequence number"
        yLabel = "Time (ms)"

        return super().plotIntervalGraph(path, id, xAxis[1:], intervals, title, xLabel, yLabel)
    
    # override
    def plotRttJitterGraph(self, path):

        id = self.getId()
        rtts = self.getRttStats().get("rtts")
        xAxis = self.getIcmpSeqsList()
        jitters = self.getJitterStats(rtts).get("jitters")
        title = None
        xLabel = "ICMP sequence number"
        yLabel = "Time (ms)"

        return super().plotRttJitterGraph(path, id, xAxis[1:], jitters, title, xLabel, yLabel)
    
    # override
    def plotIntervalJitterGraph(self, path):

        id = self.getId()
        intervals = self.getIntervalStats().get("intervals")
        xAxis = self.getIcmpSeqsList()
        jitters = self.getJitterStats(intervals).get("jitters")
        title = None
        xLabel = "ICMP sequence number"
        yLabel = "Time (ms)"

        return super().plotIntervalJitterGraph(path, id, xAxis[2:], jitters, title, xLabel, yLabel)
    
    # override
    def plotRttHistogram(self, path):

        id = self.getId()
        rtts = self.getRttStats().get("rtts")
        title = None
        xLabel = "RTT interval (ms)"
        yLabel = "Frequency"

        return super().plotRttHistogram(path, id, rtts, title, xLabel, yLabel)
    
    # override
    def plotIntervalHistogram(self, path):

        id = self.getId()
        intervals = self.getIntervalStats().get("intervals")
        title = None
        xLabel = "Packet arrival time interval (ms)"
        yLabel = "Frequency"

        return super().plotIntervalHistogram(path, id, intervals, title, xLabel, yLabel)

    # override
    def plotRttJitterHistogram(self, path):

        id = self.getId()
        rtts = self.getRttStats().get("rtts")
        jitters = self.getJitterStats(rtts).get("jitters")
        title = None
        xLabel = "Jitter interval (ms)"
        yLabel = "Frequency"

        return super().plotRttJitterHistogram(path, id, jitters, title, xLabel, yLabel)
    
    # override
    def plotIntervalJitterHistogram(self, path):

        id = self.getId()
        intervals = self.getIntervalStats().get("intervals")
        jitters = self.getJitterStats(intervals).get("jitters")
        title = None
        xLabel = "Jitter interval (ms)"
        yLabel = "Frequency"

        return super().plotIntervalJitterHistogram(path, id, jitters, title, xLabel, yLabel)
    
    #override
    def plotLossGraph(self, path):

        id = self.getId()
        lossStats = self.getLossStats().get("lossStats")
        title = None
        xLabel = "Statistics"
        yLabel = "Amount of packets"

        return super().plotLossGraph(path, id, lossStats, title, xLabel, yLabel)
    
    #override
    def plotLossRateGraph(self, path):

        id = self.getId()
        lossRate = self.getLossStats().get("lossRate")

        return super().plotLossRateGraph(path, id, lossRate)