#!/usr/bin/env python3

import argparse
import itertools
import random
import statistics
import subprocess
import sys
import time

ssh_cmd = "ssh"
cat_cmd = "cat"

class VarState:
    # https://qpp.bitbucket.io/post/streaming_algorithm/
    def __init__(self):
        self.n = 0
        self.pre = 0
        self.cur = 0
        self.m = 0
        self.s = 0
    def update(self, x):
        self.n += 1
        self.pre = self.cur
        self.cur = x / self.n + (1 - 1.0 / self.n) * self.cur
        self.m += (x - self.pre) * (x - self.cur)
        self.s += x
    def avg(self):
        return self.s / self.n
    def var(self):
        return self.m / (self.n - 1) if self.n > 1 else 0
    def stddev(self):
        import math
        return math.sqrt(self.var())

def ping(ssh_arg, n, wait, size):
    hostname = " ".join(ssh_arg)
    print(f"PING {hostname}")
    rtts = []
    vs = VarState()
    args = [ssh_cmd] + ssh_arg + [cat_cmd]
    with subprocess.Popen(args=args,
                          shell=False,
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          bufsize=0) as proc:
        for i in (range(n+1) if n > 0 else itertools.count(0)):
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
                if n > 0:
                    rtts.append(rtt)
                if i > 0:
                    vs.update(rtt)
                    mean = vs.avg()
                    std = vs.stddev()
                    print(f"seq={i} time={rtt*1000:.3f} ms, avg={mean*1000:.3f} ms, std={std*1000:.3f} ms")
                else:
                    print(f"seq={i} time={rtt*1000:.3f} ms")
                break
    rtts1 = rtts[1:]
    if len(rtts1) > 0:
        mean = statistics.mean(rtts1)
        std = statistics.stdev(rtts1, mean) if len(rtts1) >= 2 else 0
        print(f"host={hostname}: avg={mean*1000:.3f} ms, std={std*1000:.3f} ms")


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
    parser.add_argument("host",
                        metavar="HOST",
                        nargs="+",
                        help="")
    args = parser.parse_args()
    ping(args.host, args.count, args.interval, args.size)
