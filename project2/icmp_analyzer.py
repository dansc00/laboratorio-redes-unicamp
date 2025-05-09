from scapy.all import *
import numpy as np
from packet_analyzer import PacketAnalyzer
from graph_plotter import GraphPlotter
from ip_analyzer import IpAnalyzer

# analisador de pacotes em capturas .pcap
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
    # sobrescrito
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
    # sobrescrito
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
    # sobrescrito
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
    # sobrescrito
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
    
    # plota gráficos ICMP
    # sobrescrito
    def plotGraphs(self, path):

        id = self.getId()
        layers = self.getLayers()["layers"]
        nLayers = self.getLayers()["nLayers"]
        intervals = self.getIntervalStats()["intervals"]
        jitters = self.getJitterStats(intervals)["jitters"]

        seqs = self.getIcmpSeqsList()
        rtts = self.getRttStats()["rtts"]
        lossStats = self.getPacketLossStats()["lossStats"]
        lossRate = self.getPacketLossStats()["lossRate"]

        intervalGraph = GraphPlotter(xLabel="ICMP sequence number", yLabel="Time (s)")
        intervalGraph.plotLineGraph(seqs[1:], intervals, color="yellow", plotLabel="Interval between consecutive packets", marker=None)
        intervalGraph.saveGraph(path+id+"-interval.png")

        jitterGraph = GraphPlotter(xLabel="ICMP sequence number", yLabel="Time (s)")
        jitterGraph.plotLineGraph(seqs[2:], jitters, color="red", plotLabel="Variation in delay of consecutive packets (Jitter)", marker=None, autoScaleY=True, yScaleFactor=20)
        jitterGraph.saveGraph(path+id+"-jitter.png")
        
        layersGraph = GraphPlotter(xLabel="Protocol layers", yLabel="Amount of packets", legendPosition="right")
        layersGraph.plotBarGraph(layers, nLayers, plotLabel=layers)
        layersGraph.saveGraph(path+id+"-layers.png")

        rttGraph = GraphPlotter(xLabel="ICMP sequence Number", yLabel="Time (s)")
        rttGraph.plotLineGraph(seqs, rtts, color="blue", plotLabel="Round Trip Time", marker=None, autoScaleY=True)
        rttGraph.saveGraph(path+id+"-rtt.png")

        rttJitterGraph = GraphPlotter(None, "ICMP sequence number", "Time (s)")
        rttJitterGraph.plotLineGraph(seqs, rtts, color="blue", plotLabel="Round Trip Time", marker=None)
        rttJitterGraph.plotLineGraph(seqs[2:], jitters, color="red", plotLabel="Variation in delay of consecutive packets (Jitter)", marker=None, autoScaleY=True, yScaleFactor=20)
        rttJitterGraph.saveGraph(path+id+"-rtt-jitter.png")

        lossGraph = GraphPlotter(xLabel="Packet loss statistics", yLabel="Amount of packets", legendPosition="right")
        lossGraph.plotBarGraph(["sent", "received", "lost"], lossStats, ["gray", "green", "red"], ["Sent Packets", "Received Packets", "Lost Packets"])
        lossGraph.saveGraph(path+id+"-loss.png")

        lossRateGraph = GraphPlotter()
        lossRateGraph.plotPizzaGraph(["received packets", "lost packets"], [100-lossRate, lossRate], ["green", "red"])
        lossRateGraph.saveGraph(path+id+"-loss-rate.png")

    
