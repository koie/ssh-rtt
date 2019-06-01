#!/usr/bin/env python3.6

import argparse
import random
import statistics
import subprocess
import sys
import time

ssh_cmd = "ssh"
cat_cmd = "cat"


def ping(host, n, wait, size):
    print(f"PING {host}")
    rtts = []
    args = [ssh_cmd, host, cat_cmd]
    with subprocess.Popen(args=args,
                          shell=False,
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          bufsize=0) as proc:
        for i in range(n+1):
            if i > 0:
                time.sleep(wait)
            nonce = ""
            while len(nonce) < size:
                nonce = nonce + str(random.randint(0,99999999))
            nonce = nonce[:size] + "\n"
            nonce = nonce.encode()
            start = time.clock_gettime(time.CLOCK_REALTIME)
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
    if len(rtts1) > 0:
        mean = statistics.mean(rtts1)
        std = statistics.stdev(rtts1, mean) if len(rtts1) >= 2 else 0
        print(f"host={host}: avg={mean*1000:.3f} ms, std={std*1000:.3f} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ping over SSH")
    parser.add_argument("-c", "--count",
                        type=int,
                        metavar="COUNT",
                        default=10,
                        help="count")
    parser.add_argument("-i", "--interval",
                        type=float,
                        metavar="WAIT",
                        default=1,
                        help="interval")
    parser.add_argument("-s", "--size",
                        type=int,
                        metavar="SIZE",
                        default=3,
                        help="count")
    parser.add_argument("hosts",
                        metavar="HOST",
                        nargs=argparse.REMAINDER,
                        help="")
    args = parser.parse_args()
    if len(args.hosts) == 0:
        parser.print_usage(sys.stderr)
        sys.exit(1)
    for host in args.hosts:
        ping(host, args.count, args.interval, args.size)
