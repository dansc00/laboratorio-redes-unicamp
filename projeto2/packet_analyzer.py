from scapy.all import *

PATH = "capture/"

pkts = rdpcap(PATH+"capture1.pcap")

print(len(pkts))
print(pkts[1].src)
