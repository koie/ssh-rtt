#!/usr/bin/env python3.6

import time
import subprocess
import random
import argparse
import statistics

ssh_cmd = "ssh"

def ping(host, n):
    print(f"PING {host}")
    rtts = []
    args = [ssh_cmd, host, "cat"]
    with subprocess.Popen(args=args, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0) as proc:
        for i in range(n+1):
            start = time.clock_gettime(time.CLOCK_REALTIME)
            nonce = (str(random.randint(10000000,99999999)) + "\n").encode()
            proc.stdin.write(nonce)
            while True:
                nonce2 = proc.stdout.readline()
                if nonce2 != nonce:
                    continue
                end = time.clock_gettime(time.CLOCK_REALTIME)
                rtt = end - start
                print(f"seq={i} time={rtt*1000:.3f} ms")
                rtts.append(rtt)
                break
    rtts1 = rtts[1:]
    mean = statistics.mean(rtts1)
    std = statistics.stdev(rtts1, mean)
    print(f"host={host}: avg={mean*1000:.3f} ms, std={std*1000:.3f} ms")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ping over SSH")
    parser.add_argument("hosts", metavar="HOST", nargs=argparse.REMAINDER, help="")
    args = parser.parse_args()
    for host in args.hosts:
        ping(host, 10)
