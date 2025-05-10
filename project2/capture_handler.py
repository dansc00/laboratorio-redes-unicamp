from icmp_analyzer import IcmpAnalyzer

# imprime métricas e salva gráficos de todas capturas da lista
def makeAllOutput(captures):

    path = "icmpGraphs/"
    for i in range(len(captures)):
        captures[i].printMetrics()
        captures[i].plotIntervalGraph(path)
        captures[i].plotJitterGraph(path)
        captures[i].plotLayersGraph(path)
        captures[i].plotRttGraph(path)
        captures[i].plotRttJitterGraph(path)
        captures[i].plotLossGraph(path)
        captures[i].plotLossRateGraph(path)
        captures[i].plotIntervalHistogram(path)
        captures[i].plotJitterHistogram(path)
        captures[i].plotRttHistogram(path)

if __name__ == "__main__":

    path1 = "capture/h1-h3.pcap"
    path2 = "capture/h2-h4.pcap"
    capture1 = IcmpAnalyzer("h1 -> h3", path1)
    capture2 = IcmpAnalyzer("h2 -> h4", path2)

    captures = [capture1,
                capture2]
    
    makeAllOutput(captures)