from icmp_analyzer import IcmpAnalyzer

# imprime métricas e salva gráficos
def makeOutput(captures):

    for i in range(len(captures)):
        captures[i].printMetrics()
        captures[i].plotGraphs("icmpGraphs/")

if __name__ == "__main__":

    path1 = "capture/h1-h3.pcap"
    path2 = "capture/h2-h4.pcap"
    capture1 = IcmpAnalyzer("h1 -> h3", path1)
    capture2 = IcmpAnalyzer("h2 -> h4", path2)

    captures = [capture1,
                capture2]
    
    makeOutput(captures)