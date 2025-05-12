from scapy.all import *
import numpy as np
from packet_analyzer import PacketAnalyzer
from graph_plotter import GraphPlotter
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

    # retorna estatísticas de rtt ICMP: lista de rtt, desvio padrão, média, máximo, mínimo
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
        var = (std/mean)*100 if mean > 0 else 0

        return {"rtts": rtts,
                "mean": mean,
                "std": std,
                "max": max,
                "min": min,
                "var": var
                }
    
    # retorna estatísticas de intervalo de chegada entre requisições ICMP: lista de intervalos, média, desvio padrão, máximo e mínimo
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
        var = (std/mean)*100 if mean > 0 else 0

        return {"intervals": intervals,
                "mean": mean,
                "std": std,
                "max": max,
                "min": min,
                "var": var
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
        totalPackets = self.getTotalPackets()
        totalBytes = self.getTotalBytes()
        layers = self.getLayers()["layers"]
        throughput = self.getThroughput()

        return super().printGeneralMetrics(id, totalPackets, totalBytes, layers, throughput)

    # override
    def printRttMetrics(self):

        layer = "ICMP"
        mean = self.getRttStats()["mean"]
        std = self.getRttStats()["std"]
        max = self.getRttStats()["max"]
        min = self.getRttStats()["min"]
        var = self.getRttStats()["var"]

        return super().printRttMetrics(layer, mean, std, max, min, var)
    
    # override
    def printIntervalMetrics(self):

        layer = "ICMP"
        mean = self.getIntervalStats()["mean"]
        std = self.getIntervalStats()["std"]
        max = self.getIntervalStats()["max"]
        min = self.getIntervalStats()["min"]
        var = self.getIntervalStats()["var"]

        return super().printIntervalMetrics(layer, mean, std, max, min, var)
    
    # override
    def printRttJitterMetrics(self):

        layer = "ICMP"
        rtts = self.getRttStats()["rtts"]
        mean = self.getJitterStats(rtts)["mean"]
        std = self.getJitterStats(rtts)["std"]
        max = self.getJitterStats(rtts)["max"]
        min = self.getJitterStats(rtts)["min"]
        var = self.getJitterStats(rtts)["var"]

        return super().printRttJitterMetrics(layer, mean, std, max, min, var)
    
    # override
    def printIntervalJitterMetrics(self):

        layer = "ICMP"
        intervals = self.getIntervalStats()["intervals"]
        mean = self.getJitterStats(intervals)["mean"]
        std = self.getJitterStats(intervals)["std"]
        max = self.getJitterStats(intervals)["max"]
        min = self.getJitterStats(intervals)["min"]
        var = self.getJitterStats(intervals)["var"]

        return super().printIntervalJitterMetrics(layer, mean, std, max, min, var)
    
    # override
    def printLossMetrics(self):

        layer = "ICMP"
        sent = self.getLossStats()["sent"]
        received = self.getLossStats()["received"]
        lost = self.getLossStats()["lost"]
        lossRate = self.getLossStats()["lossRate"]

        return super().printLossMetrics(layer, sent, received, lost, lossRate)
    
    # plotagem de gráficos ICMP
    # override
    def plotLayersGraph(self, path):

        id = self.getId()
        layers = self.getLayers()["layers"]
        nLayers = self.getLayers()["nLayers"]
        title = None
        xLabel = "Protocol layers"
        yLabel = "Amount of packets"

        return super().plotLayersGraph(path, id, layers, nLayers, title, xLabel, yLabel)

    # override
    def plotRttGraph(self, path):

        id = self.getId()
        xAxis = self.getIcmpSeqsList()
        rtts = self.getRttStats()["rtts"]
        title = None
        xLabel = "ICMP sequence number"
        yLabel = "Time (ms)"

        return super().plotRttGraph(path, id, xAxis, rtts, title, xLabel, yLabel)
    
    # override
    def plotIntervalGraph(self, path):

        id = self.getId()
        xAxis = self.getIcmpSeqsList()
        intervals = self.getIntervalStats()["intervals"]
        title = None
        xLabel = "ICMP sequence number"
        yLabel = "Time (ms)"

        return super().plotIntervalGraph(path, id, xAxis[1:], intervals, title, xLabel, yLabel)
    
    # override
    def plotRttJitterGraph(self, path):

        id = self.getId()
        rtts = self.getRttStats()["rtts"]
        xAxis = self.getIcmpSeqsList()
        jitters = self.getJitterStats(rtts)["jitters"]
        title = None
        xLabel = "ICMP sequence number"
        yLabel = "Time (ms)"

        return super().plotRttJitterGraph(path, id, xAxis[1:], jitters, title, xLabel, yLabel)
    
    # override
    def plotIntervalJitterGraph(self, path):

        id = self.getId()
        intervals = self.getIntervalStats()["intervals"]
        xAxis = self.getIcmpSeqsList()
        jitters = self.getJitterStats(intervals)["jitters"]
        title = None
        xLabel = "ICMP sequence number"
        yLabel = "Time (ms)"

        return super().plotIntervalJitterGraph(path, id, xAxis[2:], jitters, title, xLabel, yLabel)
    
    # override
    def plotRttHistogram(self, path):

        id = self.getId()
        rtts = self.getRttStats()["rtts"]
        title = None
        xLabel = "RTT interval (ms)"
        yLabel = "Frequency"

        return super().plotRttHistogram(path, id, rtts, title, xLabel, yLabel)
    
    # override
    def plotIntervalHistogram(self, path):

        id = self.getId()
        intervals = self.getIntervalStats()["intervals"]
        title = None
        xLabel = "Packet arrival time interval (ms)"
        yLabel = "Frequency"

        return super().plotIntervalHistogram(path, id, intervals, title, xLabel, yLabel)

    # override
    def plotRttJitterHistogram(self, path):

        id = self.getId()
        rtts = self.getRttStats()["rtts"]
        jitters = self.getJitterStats(rtts)["jitters"]
        title = None
        xLabel = "Jitter interval (ms)"
        yLabel = "Frequency"

        return super().plotRttJitterHistogram(path, id, jitters, title, xLabel, yLabel)
    
    # override
    def plotIntervalJitterHistogram(self, path):

        id = self.getId()
        intervals = self.getIntervalStats()["intervals"]
        jitters = self.getJitterStats(intervals)["jitters"]
        title = None
        xLabel = "Jitter interval (ms)"
        yLabel = "Frequency"

        return super().plotIntervalJitterHistogram(path, id, jitters, title, xLabel, yLabel)
    
    #override
    def plotLossGraph(self, path):

        id = self.getId()
        lossStats = self.getLossStats()["lossStats"]
        title = None
        xLabel = "Statistics"
        yLabel = "Amount of packets"

        return super().plotLossGraph(path, id, lossStats, title, xLabel, yLabel)
    
    #override
    def plotLossRateGraph(self, path):

        id = self.getId()
        lossRate = self.getLossStats()["lossRate"]

        return super().plotLossRateGraph(path, id, lossRate)