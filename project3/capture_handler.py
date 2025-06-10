from analyzer.packet_analyzer import PacketAnalyzer

path = "capture/200701011800.dump"
pkt = PacketAnalyzer(id="dump", packetsMargin=None, path=path)

gPath = "graphs/"
pkt.plotLayersGraph(gPath, pkt.getId(), pkt.getLayers().get("layers"), pkt.getLayers().get("nLayers"), title=None, xLabel="Amount of packets", yLabel=None, 
                    legendFlag=False, horizontal=True)
pkt.printGeneralMetrics(pkt.getId(), None, None, pkt.getTotalPackets(), pkt.getTotalBytes(), pkt.getLayers().get("layers"), pkt.getThroughput())