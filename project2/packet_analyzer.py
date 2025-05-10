from scapy.all import *
from collections import Counter
import numpy as np
from graph_plotter import GraphPlotter
import sys

# analisador de pacotes em capturas .pcap
class PacketAnalyzer:

    def __init__(self, id=None, path=None):
        self.id = id

        try:
            self.packets = rdpcap(path)
        except Exception as e:
            print(f"Capture path is wrong or not specified: {e}")
            sys.exit(1)

    # retorna todos pacotes
    def getPackets(self):
        return self.packets
    
    # retorna pacote específico
    def getPacket(self, pkt):
        return self.getPackets()[pkt] if len(self.getPackets()) > 0 else 0
    
    # retorna tempo de captura de pacote
    def getTime(self, pkt):
        return float(pkt.time)
    
    # retorna id
    def getId(self):
        return self.id
    
    # retorna número total de pacotes
    def getTotalPackets(self):
        return len(self.getPackets())
    
    # retorna total de bytes capturados
    def getTotalBytes(self):
        return sum(len(pkt) for pkt in self.packets) if self.getTotalPackets() > 0 else 0
    
    # retorna tempo total de captura em s
    def getTotalTime(self):
        return self.getTimeDiff(self.getPackets()[0], self.getPackets()[-1]) if self.getTotalPackets() > 0 else 0
    
    # retorna pacotes capturados por segundo
    def getCaptureRate(self):
        return self.getTotalPackets()/self.getTotalTime() if self.getTotalTime > 0 else 0

    # recebe dois pacotes e retorna a diferença de tempo de captura entre eles
    def getTimeDiff(self, pkt1, pkt2):
        return self.getTime(pkt2) - self.getTime(pkt1)
    
    def getRttStats(self):
        pass
    
    # retorna estatísticas de intervalo de chegada entre todos pacotes: lista de intervalos, média, desvio padrão, máximo e mínimo
    def getIntervalStats(self):

        if self.getTotalPackets() < 2:
            print("There is no way to measure interval with less than two packets")
            return None

        times = []

        for pkt in self.getPackets():
            times.append(self.getTime(pkt))

        intervals = np.diff(times) if times else []  # diferença entre tempos consecutivos
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
    
    # recebe lista de intervalos de chegada entre pacotes e retorna estatísticas de jitter: lista de jitters medidos, média, desvio padrão, máximo e mínimo
    def getJitterStats(self, intervals):

        if self.getTotalPackets() < 3:
            print("There is no way to measure jitter with less than three packets")
            return None
        
        jitters = np.abs(np.diff(intervals)) if len(intervals) > 0 else []
        mean = np.mean(jitters) if len(jitters) > 0 else 0
        std = np.std(jitters) if len(jitters) > 0 else 0
        max = np.max(jitters) if len(jitters) > 0 else 0
        min = np.min(jitters) if len(jitters) > 0 else 0

        return {"jitters": jitters,
                "mean": mean,
                "std": std,
                "max": max,
                "min": min
                }
    
    def getPacketLossStats(self):
        pass

    # retorna throughput medido em Mbps
    def getThroughput(self):

        totalBits = self.getTotalBytes() * 8

        return (totalBits/self.getTotalTime())/1000000 if self.getTotalTime() > 0 else 0
    
    # retorna lista de camadas e quantidade total encontrada por camada
    def getLayers(self):
        
        layers = Counter() 

        for pkt in self.getPackets():
            while pkt:
                layers[pkt.name] += 1 # incrementa número de camadas
                pkt = pkt.payload # próxima camada, payload da camada atual

        nLayers = list(layers.values())
        layers = list(layers.keys())
        
        return {"layers": layers,
                "nLayers": nLayers
                }
    
    # salva visualização gráfica de pacote em pdf
    def packetPdfDump(self, filename, pkt):
        self.getPacket(pkt).pdfdump(filename, layer_shift=1)
    
    # imprime métricas gerais
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

        print(f"Capture {id}")
        print(f"Total packets: {total}")
        print(f"Total bytes: {totalBytes} bytes")
        print(f"Layers: {layers}")
        print(f"Mean packet arrival time: {meanInterval*1000:.2f} ms")
        print(f"Standard deviation of packet arrival time: {stdInterval*1000:.2f} ms")
        print(f"Maximum packet arrival time: {maxInterval*1000:.2f} ms")
        print(f"Minimum packet arrival time: {minInterval*1000:.2f} ms")
        print(f"Jitter mean: {meanJitter*1000:.2f} ms")
        print(f"Jitter standard deviation: {stdJitter*1000:.2f} ms")
        print(f"Maximum jitter: {maxJitter*1000:.2f} ms")
        print(f"Minimum jitter: {minJitter*1000:.2f} ms")
        print(f"Throughput: {throughput} Mbps")
        print()

    # plotagem de gráficos gerais

    def plotIntervalGraph(self, path):

        id = self.getId()
        nPackets = [i for i in range(1, self.getTotalPackets()+1)]
        intervals = self.getIntervalStats()["intervals"]

        intervalGraph = GraphPlotter(xLabel="Packet capture sequence", yLabel="Time (s)")
        intervalGraph.plotLineGraph(nPackets[1:], intervals, color="yellow", plotLabel="Interval between consecutive packets", marker=None)
        intervalGraph.saveGraph(path+id+"-interval.png")

    def plotJitterGraph(self, path):

        id = self.getId()
        nPackets = [i for i in range(1, self.getTotalPackets()+1)]
        intervals = self.getIntervalStats()["intervals"]
        jitters = self.getJitterStats(intervals)["jitters"]

        jitterGraph = GraphPlotter(xLabel="Packet capture sequence", yLabel="Time (s)")
        jitterGraph.plotLineGraph(nPackets[2:], jitters, color="red", plotLabel="Variation in delay of consecutive packets (Jitter)", marker=None, autoScaleY=True)
        jitterGraph.saveGraph(path+id+"-jitter.png")

    def plotLayersGraph(self, path):

        id = self.getId()
        layers = self.getLayers()["layers"]
        nLayers = self.getLayers()["nLayers"]

        layersGraph = GraphPlotter(xLabel="Protocol layers", yLabel="Amount of packets", legendPosition="right")
        layersGraph.plotBarGraph(layers, nLayers, plotLabel=layers)
        layersGraph.saveGraph(path+id+"-layers.png")

    def plotIntervalHistogram(self, path):

        id = self.getId()
        intervals = self.getIntervalStats()["intervals"]

        intervalHistogram = GraphPlotter(xLabel="Interval time (s)", yLabel="Frequency", legendFlag=False)
        intervalHistogram.plotHistogram(intervals, color="yellow", plotLabel="Interval between consecutive packets")
        intervalHistogram.saveGraph(path+id+"-interval-histogram.png")

    def plotJitterHistogram(self, path):

        id = self.getId()
        intervals = self.getIntervalStats()["intervals"]
        jitters = self.getJitterStats(intervals)["jitters"]

        jitterHistogram = GraphPlotter(xLabel="Jitter interval time (s)", yLabel="Frequency", legendFlag=False)
        jitterHistogram.plotHistogram(jitters, color="red", plotLabel="Variation in delay of consecutive packets (Jitter)")
        jitterHistogram.saveGraph(path+id+"-jitter-histogram.png")

    def plotRttGraph(self, path):
        pass

    def plotRttJitterGraph(self, path):
        pass

    def plotLossGraph(self, path):
        pass

    def plotLossRateGraph(self, path):
        pass

    def plotRttHistogram(self, path):
        pass

    