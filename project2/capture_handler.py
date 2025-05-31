import sys
import os

# configura raiz para importação 
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from analyzer.icmp_analyzer.icmp_analyzer import IcmpAnalyzer

# imprime métricas e salva gráficos de todas capturas da lista
def makeAllOutput(captures):

    path = "icmp_graphs/"
    for i in range(len(captures)):
        captures[i].printGeneralMetrics()
        captures[i].printRttMetrics()
        captures[i].printIntervalMetrics()
        captures[i].printRttJitterMetrics()
        captures[i].printIntervalJitterMetrics()
        captures[i].printLossMetrics()

        captures[i].plotLayersGraph(path)
        captures[i].plotRttGraph(path)
        captures[i].plotIntervalGraph(path)
        captures[i].plotRttJitterGraph(path)
        captures[i].plotIntervalJitterGraph(path)
        captures[i].plotRttHistogram(path)
        captures[i].plotIntervalHistogram(path)
        captures[i].plotRttJitterHistogram(path)
        captures[i].plotIntervalJitterHistogram(path)
        captures[i].plotLossGraph(path)
        captures[i].plotLossRateGraph(path)

if __name__ == "__main__":

    path1 = "capture/h1-h3.pcap"
    path2 = "capture/h2-h4.pcap"
    capture1 = IcmpAnalyzer("h1-h3", 10, path1)
    capture2 = IcmpAnalyzer("h2-h4", 10, path2)

    captures = [capture1,
                capture2]
    
    makeAllOutput(captures)
    '''
    capture1.getPdfDump("h1-dump.pdf", 0)
    capture1.getPdfDump("h2-dump.pdf", 1)
    capture2.getPdfDump("h3-dump.pdf", 0)
    capture2.getPdfDump("h4-dump.pdf", 1)
    '''