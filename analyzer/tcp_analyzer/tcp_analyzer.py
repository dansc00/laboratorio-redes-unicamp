from scapy.all import *
import numpy as np
from analyzer.packet_analyzer.packet_analyzer import PacketAnalyzer
from analyzer.ip_analyzer.ip_analyzer import IpAnalyzer

# analisador de camada TCP
class TcpAnalyzer(PacketAnalyzer):

    def __init__(self, id=None, packetsMargin=None, path=None):
        super().__init__(id, packetsMargin, path)
    
    # retorna número de sequência de pacote TCP
    def getTcpSeq(self, pkt):

        if TCP in pkt:
            return pkt[TCP].seq
        else:
            print("The packet doesn't have a TCP layer")
            return 0
    
    # retorna flags do TCP
    # SYN(S): pacote de inicialização de conexão (handshake)
    # ACK(A): pacote de reconhecimento
    # FIN(F): pacote de encerramento de conexão
    # RST(R): pacote de reinício de conexão
    # PSH(P): solicita que os dados sejam enviados imediatamente
    # URG(U): indica que o pacote contém dados urgentes
    def getTcpFlags(self, pkt):

        if TCP in pkt:
            return pkt[TCP].flags
        else:
            print("The packet doesn't have a TCP layer")
            return None

    # retorna lista de números de sequência TCP em ordem crescente (sem duplicatas)
    def getTcpSeqsList(self):

        seqsSet = set()
        for pkt in self.getPackets():
            if TCP in pkt:
                seqsSet.add(self.getTcpSeq(pkt))

        return sorted(list(seqsSet)) if seqsSet else []

    # retorna lista de tuplas (ip origem, ip destino, porta origem, porta destino, tcp seq) para cada pacote TCP
    def getTcpKeys(self):

        tcpKeys = set()
        for pkt in self.getPackets():
            if TCP in pkt:
                key = (
                    IpAnalyzer.getSrcIp(pkt),
                    IpAnalyzer.getDstIp(pkt),
                    pkt[TCP].sport,
                    pkt[TCP].dport,
                    pkt[TCP].seq
                )
                tcpKeys.add(key)

        return list(tcpKeys) if tcpKeys else []
    
    # retorna estatísticas de RTT baseado no handshake SYN ↔ SYN+ACK
    # override
    def getRttStats(self):
        # dicionário para armazenar timestamp de SYNs:
        syn_times = {}
        rtts = []

        for pkt in self.getPackets():
            if TCP in pkt:
                flags = self.getTcpFlags(pkt)
                src = IpAnalyzer.getSrcIp(pkt)
                dst = IpAnalyzer.getDstIp(pkt)
                sport = pkt[TCP].sport
                dport = pkt[TCP].dport
                seq = self.getTcpSeq(pkt)

                # SYN sem ACK
                if flags == "S":
                    key = (src, dst, sport, dport, seq)
                    syn_times[key] = self.getTime(pkt)

                # SYN+ACK
                elif flags == "SA":
                    # ack_num = número de sequência original + 1, então seq_request = ack - 1
                    ack_num = pkt[TCP].ack - 1
                    # chave reversa do SYN original
                    rev_key = (dst, src, dport, sport, ack_num)
                    if rev_key in syn_times:
                        # getTimeDiff retorna diferença em ms
                        rtt = self.getTimeDiff(PacketAnalyzer.getPacketByKey(self, rev_key), pkt)
                        # se getPacketByKey não existir, calculamos: (pkt.time_ms - syn_times[rev_key])
                        # mas assumimos que PacketAnalyzer.getPacketByKey busca o pacote correto
                        rtts.append(rtt)

        # agora usando "rtts" diretamente
        mean = np.mean(rtts) if rtts else 0
        std = np.std(rtts) if rtts else 0
        maximum = np.max(rtts) if rtts else 0
        minimum = np.min(rtts) if rtts else 0
        error = std / np.sqrt(len(rtts)) if len(rtts) > 0 else 0
        cv = (std / mean) * 100 if mean > 0 else 0

        return {
            "rtts": rtts,
            "mean": mean,
            "std": std,
            "max": maximum,
            "min": minimum,
            "error": error,
            "cv": cv
        }
    
    # retorna estatísticas de intervalo de chegada entre pacotes SYN
    # override
    def getIntervalStats(self):
        if self.getTotalPackets() < 2:
            print("There is no way to measure interval with less than two packets")
            return None

        syn_times = []
        for pkt in self.getPackets():
            if TCP in pkt and self.getTcpFlags(pkt) == "S":
                syn_times.append(self.getTime(pkt))

        intervals = np.diff(np.array(syn_times)) if len(syn_times) > 1 else np.array([])
        mean = np.mean(intervals) if intervals.size > 0 else 0
        std = np.std(intervals) if intervals.size > 0 else 0
        maximum = np.max(intervals) if intervals.size > 0 else 0
        minimum = np.min(intervals) if intervals.size > 0 else 0
        error = std / np.sqrt(intervals.size) if intervals.size > 0 else 0
        cv = (std / mean) * 100 if mean > 0 else 0

        return {
            "intervals": intervals,
            "mean": mean,
            "std": std,
            "max": maximum,
            "min": minimum,
            "error": error,
            "cv": cv
        }

    # retorna estatísticas de perda/retransmissão de pacotes TCP
    # override
    def getLossStats(self):
        total = 0
        seq_counts = {}
        for pkt in self.getPackets():
            if TCP in pkt:
                total += 1
                key = (
                    IpAnalyzer.getSrcIp(pkt),
                    IpAnalyzer.getDstIp(pkt),
                    pkt[TCP].sport,
                    pkt[TCP].dport,
                    pkt[TCP].seq
                )
                seq_counts[key] = seq_counts.get(key, 0) + 1

        # retransmissões ocorrem quando count > 1 para um mesmo key
        retransmissions = sum(count - 1 for count in seq_counts.values() if count > 1)
        received_unique = len(seq_counts)
        loss_rate = (retransmissions * 100) / total if total > 0 else 0

        return {
            "totalPackets": total,
            "uniquePackets": received_unique,
            "retransmissions": retransmissions,
            "lossRate": loss_rate
        }

    # imprime métricas TCP
    # override
    def printGeneralMetrics(self):
        id = self.getId()
        keys = self.getTcpKeys()
        totalPackets = self.getTotalPackets()
        totalBytes = self.getTotalBytes()
        layers = self.getLayers().get("layers")
        throughput = self.getThroughput()

        print("TCP keys (src, dst, sport, dport, seq):")
        for key in keys:
            print(key)

        return super().printGeneralMetrics(id, totalPackets, totalBytes, layers, throughput)

    # override
    def printRttMetrics(self):
        layer = "TCP"
        stats = self.getRttStats()
        mean = stats.get("mean")
        std = stats.get("std")
        maximum = stats.get("max")
        minimum = stats.get("min")
        error = stats.get("error")
        cv = stats.get("cv")

        return super().printRttMetrics(layer, mean, std, maximum, minimum, error, cv)

    # override
    def printIntervalMetrics(self):
        layer = "TCP"
        stats = self.getIntervalStats()
        mean = stats.get("mean")
        std = stats.get("std")
        maximum = stats.get("max")
        minimum = stats.get("min")
        error = stats.get("error")
        cv = stats.get("cv")

        return super().printIntervalMetrics(layer, mean, std, maximum, minimum, error, cv)

    # override
    def printLossMetrics(self):
        layer = "TCP"
        stats = self.getLossStats()
        total = stats.get("totalPackets")
        unique = stats.get("uniquePackets")
        retrans = stats.get("retransmissions")
        lossRate = stats.get("lossRate")

        return super().printLossMetrics(layer, total, unique, retrans, lossRate)

    # plotagem de gráficos TCP
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
        xAxis = self.getTcpSeqsList()
        rtts = self.getRttStats().get("rtts")
        title = None
        xLabel = "TCP sequence number"
        yLabel = "RTT (ms)"
        return super().plotRttGraph(path, id, xAxis, rtts, title, xLabel, yLabel)

    # override
    def plotIntervalGraph(self, path):
        id = self.getId()
        xAxis = self.getTcpSeqsList()
        intervals = self.getIntervalStats().get("intervals")
        title = None
        xLabel = "TCP sequence number"
        yLabel = "Interval between SYNs (ms)"
        return super().plotIntervalGraph(path, id, xAxis[1:], intervals, title, xLabel, yLabel)

    # override
    def plotRttHistogram(self, path):
        id = self.getId()
        rtts = self.getRttStats().get("rtts")
        title = None
        xLabel = "RTT (ms)"
        yLabel = "Frequency"
        return super().plotRttHistogram(path, id, rtts, title, xLabel, yLabel)

    # override
    def plotIntervalHistogram(self, path):
        id = self.getId()
        intervals = self.getIntervalStats().get("intervals")
        title = None
        xLabel = "Interval (ms)"
        yLabel = "Frequency"
        return super().plotIntervalHistogram(path, id, intervals, title, xLabel, yLabel)

    # override
    def plotLossGraph(self, path):
        id = self.getId()
        stats = self.getLossStats()
        lossStats = [stats.get("totalPackets"), stats.get("uniquePackets"), stats.get("retransmissions")]
        title = None
        xLabel = "Total, Unique, Retrans"
        yLabel = "Packet Count"
        return super().plotLossGraph(path, id, lossStats, title, xLabel, yLabel)

    # override
    def plotLossRateGraph(self, path):
        id = self.getId()
        lossRate = self.getLossStats().get("lossRate")
        return super().plotLossRateGraph(path, id, lossRate)
