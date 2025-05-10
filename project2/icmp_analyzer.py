from scapy.all import *
import numpy as np
from packet_analyzer import PacketAnalyzer
from graph_plotter import GraphPlotter
from ip_analyzer import IpAnalyzer

# analisador de camada ICMP
class IcmpAnalyzer(PacketAnalyzer):

    def __init__(self, id=None, path=None):
        super().__init__(id, path)
    
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

    # retorna estatísticas de RTT ICMP: lista de RTT, desvio padrão, média, máximo, mínimo
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

        return {"rtts": rtts,
                "mean": mean,
                "std": std,
                "max": max,
                "min": min
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

        return {"intervals": intervals,
                "mean": mean,
                "std": std,
                "max": max,
                "min": min
                } 
    
    # retorna estatísticas de perda de pacotes: enviados, recebidos, perdidos, taxa de perdas
    # override
    def getPacketLossStats(self):

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
    def printMetrics(self):

        id = self.getId()
        total = self.getTotalPackets()
        totalBytes = self.getTotalBytes()
        layers = self.getLayers()["layers"]
        intervals = self.getIntervalStats()["intervals"]
        meanInterval = self.getIntervalStats()["mean"]
        stdInterval = self.getIntervalStats()["std"]
        maxInterval = self.getIntervalStats()["max"]
        minInterval = self.getIntervalStats()["min"]
        meanJitter = self.getJitterStats(intervals)["mean"]
        stdJitter = self.getJitterStats(intervals)["std"]
        maxJitter = self.getJitterStats(intervals)["max"]
        minJitter = self.getJitterStats(intervals)["min"]
        throughput = self.getThroughput()

        src = IpAnalyzer.getSrcIp(self.getPacket(0))
        dst = IpAnalyzer.getDstIp(self.getPacket(0))
        meanRtt = self.getRttStats()["mean"]
        stdRtt = self.getRttStats()["std"]
        maxRtt = self.getRttStats()["max"]
        minRtt = self.getRttStats()["min"]
        sent = self.getPacketLossStats()["sent"]
        received = self.getPacketLossStats()["received"]
        lost = self.getPacketLossStats()["lost"]
        lossRate = self.getPacketLossStats()["lossRate"]

        print(f"Capture {id}")
        print(f"Total packets: {total}")
        print(f"Total bytes: {totalBytes} bytes")
        print(f"Source IPv4: {src}")
        print(f"Destination IPv4: {dst}")
        print(f"Layers: {layers}")
        print(f"Mean ICMP request packet arrival time: {meanInterval*1000:.2f} ms")
        print(f"Standard deviation of ICMP request packet arrival time: {stdInterval*1000:.2f} ms")
        print(f"Maximum ICMP request packet arrival time: {maxInterval*1000:.2f} ms")
        print(f"Minimum ICMP request packet arrival time: {minInterval*1000:.2f} ms")
        print(f"Jitter mean: {meanJitter*1000:.2f} ms")
        print(f"Jitter standard deviation: {stdJitter*1000:.2f} ms")
        print(f"Maximum jitter: {maxJitter*1000:.2f} ms")
        print(f"Minimum jitter: {minJitter*1000:.2f} ms")
        print(f"Throughput: {throughput:.4f} Mbps")
        print(f"Mean ICMP RTT: {meanRtt*1000:.2f} ms")
        print(f"ICMP RTT standard deviation: {stdRtt*1000:.2f} ms")
        print(f"Maximum ICMP RTT: {maxRtt*1000:.2f} ms")
        print(f"Minimum ICMP RTT: {minRtt*1000:.2f} ms")
        print(f"Sent packets: {sent}")
        print(f"Received packets: {received}")
        print(f"Lost packets: {lost}")
        print(f"Loss rate: {lossRate}%")
        print()
    
    # plotagem de gráficos ICMP
    # override
    def plotIntervalGraph(self, path):
        
        id = self.getId()
        seqs = self.getIcmpSeqsList()
        intervals = self.getIntervalStats()["intervals"]

        intervalGraph = GraphPlotter(xLabel="ICMP sequence number", yLabel="Time (s)")
        intervalGraph.plotLineGraph(seqs[1:], intervals, color="yellow", plotLabel="ICMP request packet arrival time interval", marker=None)
        intervalGraph.saveGraph(path+id+"-interval.png")
    
    # override
    def plotJitterGraph(self, path):

        id = self.getId()
        seqs = self.getIcmpSeqsList()
        intervals = self.getIntervalStats()["intervals"]
        jitters = self.getJitterStats(intervals)["jitters"]

        jitterGraph = GraphPlotter(xLabel="ICMP sequence number", yLabel="Time (s)")
        jitterGraph.plotLineGraph(seqs[2:], jitters, color="red", plotLabel="Variation in ICMP request packet arrival time interval (Jitter)", marker=None, autoScaleY=True)
        jitterGraph.saveGraph(path+id+"-jitter.png")
    
    #override
    def plotLayersGraph(self, path):

        id = self.getId()
        layers = self.getLayers()["layers"]
        nLayers = self.getLayers()["nLayers"]

        layersGraph = GraphPlotter(xLabel="Protocol layers", yLabel="Amount of packets", legendPosition="right")
        layersGraph.plotBarGraph(layers, nLayers, plotLabel=layers)
        layersGraph.saveGraph(path+id+"-layers.png")

    # override
    def plotRttGraph(self, path):
        
        id = self.getId()
        seqs = self.getIcmpSeqsList()
        rtts = self.getRttStats()["rtts"]

        rttGraph = GraphPlotter(xLabel="ICMP sequence Number", yLabel="Time (s)")
        rttGraph.plotLineGraph(seqs, rtts, color="blue", plotLabel="Round Trip Time", marker=None, autoScaleY=True)
        rttGraph.saveGraph(path+id+"-rtt.png")

    #override
    def plotRttJitterGraph(self, path):

        id = self.getId()
        seqs = self.getIcmpSeqsList()
        rtts = self.getRttStats()["rtts"]
        intervals = self.getIntervalStats()["intervals"]
        jitters = self.getJitterStats(intervals)["jitters"]

        rttJitterGraph = GraphPlotter(xLabel="ICMP sequence number", yLabel="Time (s)")
        rttJitterGraph.plotLineGraph(seqs, rtts, color="blue", plotLabel="Round Trip Time", marker=None)
        rttJitterGraph.plotLineGraph(seqs[2:], jitters, color="red", plotLabel="Variation in ICMP request packet arrival time interval (Jitter)", marker=None, autoScaleY=True)
        rttJitterGraph.saveGraph(path+id+"-rtt-jitter.png")
    
    # override
    def plotLossGraph(self, path):

        id = self.getId()
        lossStats = self.getPacketLossStats()["lossStats"]

        lossGraph = GraphPlotter(xLabel="Packet loss statistics", yLabel="Amount of packets", legendPosition="right")
        lossGraph.plotBarGraph(["sent", "received", "lost"], lossStats, ["gray", "green", "red"], ["Sent Packets", "Received Packets", "Lost Packets"])
        lossGraph.saveGraph(path+id+"-loss.png")
    
    # override
    def plotLossRateGraph(self, path):
        
        id = self.getId()
        lossRate = self.getPacketLossStats()["lossRate"]

        lossRateGraph = GraphPlotter()
        lossRateGraph.plotPizzaGraph(["received packets", "lost packets"], [100-lossRate, lossRate], ["green", "red"])
        lossRateGraph.saveGraph(path+id+"-loss-rate.png")

    # override
    def plotIntervalHistogram(self, path):

        id = self.getId()
        intervals = self.getIntervalStats()["intervals"]

        intervalHistogram = GraphPlotter(xLabel="Interval time (s)", yLabel="Frequency", legendFlag=False)
        intervalHistogram.plotHistogram(intervals, color="yellow", plotLabel="ICMP request packet arrival time interval")
        intervalHistogram.saveGraph(path+id+"-interval-histogram.png")
    
    #override
    def plotJitterHistogram(self, path):

        id = self.getId()
        intervals = self.getIntervalStats()["intervals"]
        jitters = self.getJitterStats(intervals)["jitters"]

        jitterHistogram = GraphPlotter(xLabel="Jitter interval time (s)", yLabel="Frequency", legendFlag=False)
        jitterHistogram.plotHistogram(jitters, color="red", plotLabel="Variation in ICMP request packet arrival time interval (Jitter)")
        jitterHistogram.saveGraph(path+id+"-jitter-histogram.png")

    #override
    def plotRttHistogram(self, path):
        
        id = self.getId()
        rtts = self.getRttStats()["rtts"]

        rttHistogram = GraphPlotter(xLabel="RTT interval time (s)", yLabel="Frequency", legendFlag=False)
        rttHistogram.plotHistogram(rtts, color="blue", plotLabel="Round Trip Time")
        rttHistogram.saveGraph(path+id+"-rtt-histogram.png")
        

        
        
    
