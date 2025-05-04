#!/bin/bash

# busca pacotes de captura no servidor ssh da vm mininet
scp mininet@192.168.122.7:/home/mininet/h1-h3.pcap /home/daniel/mc833/projeto2/capture
scp mininet@192.168.122.7:/home/mininet/h2-h4.pcap /home/daniel/mc833/projeto2/capture
scp mininet@192.168.122.7:/home/mininet/h1-s1-h3.pcap /home/daniel/mc833/projeto2/capture
scp mininet@192.168.122.7:/home/mininet/h2-s1-h4.pcap /home/daniel/mc833/projeto2/capture
