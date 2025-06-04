from scapy.all import *
from collections import Counter
import numpy as np
from analyzer.graph_plotter.graph_plotter import GraphPlotter
import sys

# analisador de pacotes em capturas .pcap
class PacketAnalyzer():

    def __init__(self, id=None, packetsMargin=None, path=None):
        self.id = id
        self.packetsMargin = packetsMargin

        try:
            self.packets = rdpcap(path)
        except Exception as e:
            print(f"Capture path is wrong or not specified: {e}")
            sys.exit(1)

    # retorna pacotes, pode excluir os n primeiros e n últimos para evitar viés de borda
    def getPackets(self):

        if self.packetsMargin != None:
            return self.packets[self.packetsMargin:-self.packetsMargin]
        else:
            return self.packets
    
    # retorna pacote específico
    def getPacket(self, pkt):
        return self.getPackets()[pkt] if len(self.getPackets()) > 0 else 0
    
    # retorna tempo de captura de pacote em ms
    def getTime(self, pkt):
        return float(pkt.time*1000)
    
    # retorna id
    def getId(self):
        return self.id
    
    # retorna número total de pacotes
    def getTotalPackets(self):
        return len(self.getPackets())
    
    # retorna total de bytes capturados
    def getTotalBytes(self):
        return sum(len(pkt) for pkt in self.getPackets()) if self.getTotalPackets() > 0 else 0
    
    # retorna tempo total de captura em ms
    def getTotalTime(self):
        return self.getTimeDiff(self.getPackets()[0], self.getPackets()[-1]) if self.getTotalPackets() > 0 else 0
    
    # retorna pacotes capturados por segundo
    def getCaptureRate(self):
        return self.getTotalPackets()/self.getTotalTime() if self.getTotalTime > 0 else 0

    # recebe dois pacotes e retorna a diferença de tempo de captura entre eles
    def getTimeDiff(self, pkt1, pkt2):
        return self.getTime(pkt2) - self.getTime(pkt1)
    
    # retorna throughput medido em Mbps
    def getThroughput(self):

        totalBits = self.getTotalBytes() * 8

        return (totalBits/self.getTotalTime())/1000 if self.getTotalTime() > 0 else 0
    
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
    
    # retorna estatísticas de jitter baseado na variação de dados: lista de jitters, média, desvio padrão, máximo, mínimo, erro padrão e coeficiente de variação
    def getJitterStats(self, data):
        
        if self.getTotalPackets() < 3:
            print("There is no way to measure jitter with less than three packets")
            return None
        
        jitters = np.abs(np.diff(data)) if len(data) > 0 else []
        mean = np.mean(jitters) if len(jitters) > 0 else 0
        std = np.std(jitters) if len(jitters) > 0 else 0
        max = np.max(jitters) if len(jitters) > 0 else 0
        min = np.min(jitters) if len(jitters) > 0 else 0
        error = std/np.sqrt(len(jitters)) if len(jitters) > 0 else 0
        cv = (std/mean)*100 if mean > 0 else 0

        return {"jitters": jitters,
                "mean": mean,
                "std": std,
                "max": max,
                "min": min,
                "error": error,
                "cv": cv
                }
    
    # salva visualização gráfica de pacote em pdf
    def getPdfDump(self, filename, pkt):
        self.getPacket(pkt).pdfdump(filename, layer_shift=1)
    
    def getRttStats(self):
        pass
    
    def getIntervalStats(self):
        pass
    
    def getLossStats(self):
        pass

    # retorna quantidade correta de casas decimais para representação (value ± error)
    @staticmethod
    def getDecimalPlaces(error):

        if error == 0:
            return 0
        
        places = np.floor(np.log10(np.abs(error)))

        return max(0, int(-places))

    # imprime métricas gerais
    def printGeneralMetrics(self, id, totalPackets, totalBytes, layers, throughput):

        print(f"Capture {id}")
        print(f"Total packets: {totalPackets}")
        print(f"Total bytes: {totalBytes} bytes")
        print(f"Layers: {layers}")
        print(f"Throughput: {throughput:.4f} Mbps\n")

    # imprime métricas de RTT
    def printRttMetrics(self, layer, mean, std, max, min, error, cv):
        
        places = self.getDecimalPlaces(error)
        print(f"Mean {layer} RTT: {mean:.{places}f} ms")
        print(f"{layer} RTT standard deviation: {std:.{places}f} ms")
        print(f"Maximum {layer} RTT: {max:.{places}f} ms")
        print(f"Minimum {layer} RTT: {min:.{places}f} ms")
        print(f"Standard error: {error:.{places}f} ms")
        print(f"Percentage of standard deviation from the mean: {cv:.2f}%\n")
    
    # imprime métricas de intervalo de chegada entre pacotes
    def printIntervalMetrics(self, layer, mean, std, max, min, error, cv):

        places = self.getDecimalPlaces(error)
        print(f"Mean {layer} packets arrival time interval: {mean:.{places}f} ms")
        print(f"Standard deviation of {layer} packets arrival time interval: {std:.{places}f} ms")
        print(f"Maximum {layer} packet arrival time interval: {max:.{places}f} ms")
        print(f"Minimum {layer} request packet arrival time Interval: {min:.{places}f} ms")
        print(f"Standard error: {error:.{places}f} ms")
        print(f"Percentage of standard deviation from the mean: {cv:.2f}%\n")

    # imprime métricas de jitter baseado em rtt
    def printRttJitterMetrics(self, layer, mean, std, max, min, error, cv):

        places = self.getDecimalPlaces(error)
        print(f"{layer} RTT based jitter mean: {mean:.{places}f} ms")
        print(f"{layer} RTT based jitter standard deviation: {std:.{places}f} ms")
        print(f"{layer} RTT based maximum jitter: {max:.{places}f} ms")
        print(f"{layer} RTT based minimum jitter: {min:.{places}f} ms")
        print(f"Standard error: {error:.{places}f} ms")
        print(f"Percentage of standard deviation from the mean: {cv:.2f}%\n")

    # imprime métricas de jitter baseado em intervalo de chegada
    def printIntervalJitterMetrics(self, layer, mean, std, max, min, error, cv):

        places = self.getDecimalPlaces(error)
        print(f"{layer} arrival time interval based jitter mean: {mean:.{places}f} ms")
        print(f"{layer} arrival time interval based jitter standard deviation: {std:.{places}f} ms")
        print(f"{layer} arrival time interval based maximum jitter: {max:.{places}f} ms")
        print(f"{layer} arrival time interval based minimum jitter: {min:.{places}f} ms")
        print(f"Standard error: {error:.{places}f} ms")
        print(f"Percentage of standard deviation from the mean: {cv:.2f}%\n")
    
    # imprime métricas de perda de pacotes
    def printLossMetrics(self, layer, sent, received, lost, lossRate):

        print(f"{layer} sent packets: {sent}")
        print(f"{layer} received packets: {received}")
        print(f"{layer} lost packets: {lost}")
        print(f"{layer} loss rate: {lossRate}%\n")
        print("-------------------------------------------------------------------")

    # plota gráfico de barra para o total de camadas
    def plotLayersGraph(self, path, id, layers, nLayers, title=None, xLabel=None, yLabel=None, legendFlag=True, horizontal=False):

        layersGraph = GraphPlotter(title=title, xLabel=xLabel, yLabel=yLabel, legendFlag=legendFlag, legendPosition="right")
        layersGraph.plotBarGraph(layers, nLayers, plotLabel=layers, horizontal=horizontal)
        layersGraph.saveGraph(path+id+"-layers.png")

    # plota gráfico de rtt 
    def plotRttGraph(self, path, id, xAxis, rtts, title=None, xLabel=None, yLabel=None):

        rttGraph = GraphPlotter(title=title, xLabel=xLabel, yLabel=yLabel)
        rttGraph.plotLineGraph(xAxis, rtts, color="blue", plotLabel="Round Trip Time", marker=None, autoScaleY=True)
        rttGraph.saveGraph(path+id+"-rtt.png")

    # plota gráfico de intervalos de chegada entre pacotes
    def plotIntervalGraph(self, path, id, xAxis, intervals, title=None, xLabel=None, yLabel=None):

        intervalGraph = GraphPlotter(title=title, xLabel=xLabel, yLabel=yLabel)
        intervalGraph.plotLineGraph(xAxis, intervals, color="yellow", plotLabel="Packets arrival time interval", marker=None)
        intervalGraph.saveGraph(path+id+"-interval.png")

    # plota gráfico de jitter baseado em rtt
    def plotRttJitterGraph(self, path, id, xAxis, jitters, title=None, xLabel=None, yLabel=None):

        rttJitterGraph = GraphPlotter(title=title, xLabel=xLabel, yLabel=yLabel)
        rttJitterGraph.plotLineGraph(xAxis, jitters, color="red", plotLabel="RTT based Jitter", marker=None)
        rttJitterGraph.saveGraph(path+id+"-rtt-jitter.png")

    # plota gráfico de jitter baseado em intervalo de chegada
    def plotIntervalJitterGraph(self, path, id, xAxis, jitters, title=None, xLabel=None, yLabel=None):
        
        intervalJitterGraph = GraphPlotter(title=title, xLabel=xLabel, yLabel=yLabel)
        intervalJitterGraph.plotLineGraph(xAxis, jitters, color="orange", plotLabel="Arrival time interval based Jitter", marker=None)
        intervalJitterGraph.saveGraph(path+id+"-interval-jitter.png")

    # plota histograma de rtt
    def plotRttHistogram(self, path, id, rtts, title=None, xLabel=None, yLabel=None):
        
        rttHistogram = GraphPlotter(title=title, xLabel=xLabel, yLabel=yLabel, legendFlag=False)
        rttHistogram.plotHistogram(rtts, color="blue")
        rttHistogram.saveGraph(path+id+"-rtt-histogram.png")
    
    # plota histograma de intervalos de chegada
    def plotIntervalHistogram(self, path, id, intervals, title=None, xLabel=None, yLabel=None):
        
        intervalHistogram = GraphPlotter(title=title, xLabel=xLabel, yLabel=yLabel, legendFlag=False)
        intervalHistogram.plotHistogram(intervals, color="yellow")
        intervalHistogram.saveGraph(path+id+"-interval-histogram.png")

    # plota histograma de jitter baseado em rtt
    def plotRttJitterHistogram(self, path, id, jitters, title=None, xLabel=None, yLabel=None):

        jitterHistogram = GraphPlotter(title=title, xLabel=xLabel, yLabel=yLabel, legendFlag=False)
        jitterHistogram.plotHistogram(jitters, color="red")
        jitterHistogram.saveGraph(path+id+"-rtt-jitter-histogram.png")

    # plota histogram de jitter baseado em intervalo de chegada
    def plotIntervalJitterHistogram(self, path, id, jitters, title=None, xLabel=None, yLabel=None):

        jitterHistogram = GraphPlotter(title=title, xLabel=xLabel, yLabel=yLabel, legendFlag=False)
        jitterHistogram.plotHistogram(jitters, color="orange")
        jitterHistogram.saveGraph(path+id+"-interval-jitter-histogram.png")
    
    # plota gráfico de perda de pacotes
    def plotLossGraph(self, path, id, lossStats, title=None, xLabel=None, yLabel=None):
        
        lossGraph = GraphPlotter(title=title, xLabel=xLabel, yLabel=yLabel, legendPosition="right")
        lossGraph.plotBarGraph(["sent", "received", "lost"], lossStats, ["gray", "green", "red"], ["Sent Packets", "Received Packets", "Lost Packets"])
        lossGraph.saveGraph(path+id+"-loss.png")

    # plota gráfico de porcentagem de perda de pacotes
    def plotLossRateGraph(self, path, id, lossRate):
        
        lossRateGraph = GraphPlotter()
        lossRateGraph.plotPizzaGraph(["received packets", "lost packets"], [100-lossRate, lossRate], ["green", "red"])
        lossRateGraph.saveGraph(path+id+"-loss-rate.png")

    

    