from scapy.all import *
from collections import Counter
from packet_analyzer import PacketAnalyzer
from graph_plotter import GraphPlotter
import sys

# manipulador de captura de pacotes .pcap
class CaptureHandler:

    def __init__(self, path=None, id=None):
        self.id = id

        try:
            self.cpt = rdpcap(path)
        except Exception as e:
            print(f"File read error: {e}")
            sys.exit(1)

    # retorna id
    def getId(self):
        return self.id
    
    # retorna pacotes na captura
    def getPackets(self):
        return self.cpt

    # retorna número total de pacotes na captura
    def getTotalPackets(self):
        return len(self.cpt)
    
    # retorna lista de layers e quantidade total encontrada
    def getLayers(self):
        
        layers = Counter() 

        for pkt in self.cpt:
            while pkt:
                layers[pkt.name] += 1 # incrementa número de camadas
                pkt = pkt.payload # próxima camada, payload da camada atual

        nLayers = list(layers.values())
        layers = list(layers.keys())
        
        return {"layers": layers,
                "nLayers": nLayers}
    
    # salva visualização gráfica do pacote referido por argumento
    def pdfDump(self, filename, nPkt):
        self.cpt[nPkt].pdfdump(filename, layer_shift=1)
    
    # imprime métricas de captura
    def printMetrics(self):

        id = self.getId()
        total = self.getTotalPackets()
        layers = self.getLayers()["layers"]

        print(f"Capture {id}")
        print(f"Total packets: {total}")
        print(f"Layers: {layers}")
        print()

if __name__ == "__main__":

    def buildAnalyzers(captures):

        analyzers = []
        for i in range(len(captures)):
            analyzer = PacketAnalyzer(captures[i].getPackets())
            analyzers.append(analyzer)
        
        return analyzers
    
    def printMetrics(captures, analyzers):

        for i in range(len(analyzers)):
            captures[i].printMetrics()
            analyzers[i].printIcmpMetrics()
    
    def plotIcmpGraphs(captures, analyzers, path):

        for i in range(len(analyzers)):
            dst = path+"{}-"+f"{captures[i].getId()}"+".png"

            seqs = analyzers[i].getIcmpSeqsList()
            rtts = analyzers[i].getIcmpRttStats()["rtts"]
            jitters = analyzers[i].getJitterStats(analyzers[i].getIcmpIntervalStats()["intervals"])["jitters"]
            intervals = analyzers[i].getIcmpIntervalStats()["intervals"]
            sent = analyzers[i].getIcmpPacketLossStats()["sent"]
            received = analyzers[i].getIcmpPacketLossStats()["received"]
            lost = analyzers[i].getIcmpPacketLossStats()["lost"]
            lossRate = analyzers[i].getIcmpPacketLossStats()["lossRate"]
            lossStats = [sent, received, lost]
            layers = captures[i].getLayers()["layers"]
            nLayers = captures[i].getLayers()["nLayers"]

            rttGraph = GraphPlotter(None, "ICMP sequence Number", "Time (s)")
            rttGraph.plotLineGraph(seqs, rtts, color="blue", plotLabel="Round Trip Time", marker=None, autoScaleY=True)
            rttGraph.saveGraph(dst.format("rtt"))

            jitterGraph = GraphPlotter(None, "ICMP sequence number", "Time (s)")
            jitterGraph.plotLineGraph(seqs[2:], jitters, color="red", plotLabel="Variation in delay of consecutive packets (Jitter)", marker=None, autoScaleY=True, scaleFactor=20)
            jitterGraph.saveGraph(dst.format("jitter"))

            intervalGraph = GraphPlotter(None, "ICMP sequence number", "Time (s)")
            intervalGraph.plotLineGraph(seqs[1:], intervals, color="yellow", plotLabel="Interval between consecutive arriving packets", marker=None)
            intervalGraph.saveGraph(dst.format("interval"))

            rttJitterGraph = GraphPlotter(None, "ICMP sequence number", "Time (s)")
            rttJitterGraph.plotLineGraph(seqs, rtts, color="blue", plotLabel="Round Trip Time", marker=None)
            rttJitterGraph.plotLineGraph(seqs[2:], jitters, color="red", plotLabel="Variation in delay of consecutive packets (Jitter)", marker=None, autoScaleY=True, scaleFactor=20)
            rttJitterGraph.saveGraph(dst.format("rtt-jitter"))

            lossGraph = GraphPlotter(None, "Packet loss statistics", "Amount of packets", legendPosition="right")
            lossGraph.plotBarGraph(["sent", "received", "lost"], lossStats, ["gray", "green", "red"], ["Sent Packets", "Received Packets", "Lost Packets"])
            lossGraph.saveGraph(dst.format("loss"))

            lossRateGraph = GraphPlotter()
            lossRateGraph.plotPizzaGraph(["received packets", "lost packets"], [100-lossRate, lossRate], ["green", "red"])
            lossRateGraph.saveGraph(dst.format("loss-rate"))

            layersGraph = GraphPlotter(None, "Protocol layers", "Amount of packets", legendPosition="right")
            layersGraph.plotBarGraph(layers, nLayers, plotLabel=layers)
            layersGraph.saveGraph(dst.format("layers"))

    path1 = "capture/h1-h3.pcap"
    path2 = "capture/h2-h4.pcap"
    capture1 = CaptureHandler(path1, "h1 -> h3")
    capture2 = CaptureHandler(path2, "h2 -> h4")

    captures = [capture1,
                capture2]
    
    analyzers = buildAnalyzers(captures)
    printMetrics(captures, analyzers)
    plotIcmpGraphs(captures, analyzers, "graphs/")

    capture1.pdfDump("dump1.pdf", 0)
    capture2.pdfDump("dump2.pdf", 0)