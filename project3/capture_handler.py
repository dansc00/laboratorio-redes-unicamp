import sys
import os

# configura raiz para importação 
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from analyzer.packet_analyzer.packet_analyzer import PacketAnalyzer

path = "capture/200701011800.dump"
pkt = PacketAnalyzer("dump", None, path)

gPath = "graphs/"
pkt.plotLayersGraph(gPath, pkt.getId(), pkt.getLayers().get("layers"), pkt.getLayers().get("nLayers"), title=None, xLabel="Amount of packets", yLabel=None, 
                    legendFlag=False, horizontal=True)
pkt.printGeneralMetrics(pkt.getId(), None, None, pkt.getTotalPackets(), pkt.getTotalBytes(), pkt.getLayers().get("layers"), pkt.getThroughput())