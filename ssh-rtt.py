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

coloring = True
threshold1 = "> mean + std"
threshold2 =  "> mean + 2 * std"


class VarState:
    # https://qpp.bitbucket.io/post/streaming_algorithm/
    def __init__(self):
        self.n = 0
        self.pre = 0
        self.cur = 0
        self.m = 0
        self.s = 0
        self.min = 0
        self.max = 0
    def update(self, x):
        self.n += 1
        self.pre = self.cur
        self.cur = x / self.n + (1 - 1.0 / self.n) * self.cur
        self.m += (x - self.pre) * (x - self.cur)
        self.s += x
        if self.n > 1:
            self.min = min(self.min, x)
            self.max = max(self.max, x)
        else:
            self.min = self.max = x
    def avg(self):
        return self.s / self.n
    def var(self):
        return self.m / (self.n - 1) if self.n > 1 else 0
    def stddev(self):
        import math
        return math.sqrt(self.var())


class Color:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    END = '\033[0m'


def ping(ssh_arg, n, wait, size):
    hostname = " ".join(ssh_arg)
    print(f"PING {hostname}", flush=True)
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
                if coloring and i >= 10:
                    if eval("rtt " + threshold2):
                        print(Color.RED, end="")
                    elif eval("rtt " + threshold1):
                        print(Color.YELLOW, end="")
                    else:
                        print(Color.END, end="")
                if i > 0:
                    vs.update(rtt)  # because first rtt may be slow, discard it.
                    mean = vs.avg()
                    std = vs.stddev()
                print(f"seq={i} time={rtt*1000:.3f} ms", end="")
                if i > 0:
                    print(f", min={vs.min*1000:.3f} ms, avg={mean*1000:.3f} ms, max={vs.max*1000:.3f} ms, std={std*1000:.3f} ms", end="")
                print(Color.END, flush=True)
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ping over SSH")
    parser.add_argument("-c", "--count",
                        type=int,
                        metavar="COUNT",
                        default=10,
                        help="")
    parser.add_argument("-i", "--interval",
                        type=float,
                        metavar="WAIT",
                        default=1,
                        help="")
    parser.add_argument("-s", "--size",
                        type=int,
                        metavar="SIZE",
                        default=3,
                        help="")
    parser.add_argument("--color",
                        action="store_true",
                        help="")
    parser.add_argument("--no-color",
                        action="store_true",
                        help="")
    parser.add_argument("--threshold1",
                        type=str,
                        default=threshold1,
                        help="")
    parser.add_argument("--threshold2",
                        type=str,
                        default=threshold2,
                        help="")
    parser.add_argument("host",
                        metavar="HOST",
                        nargs="+",
                        help="")
    args = parser.parse_args()

    if args.color:
        coloring = True
    elif args.no_color:
        coloring = False
    else:
        coloring = sys.stdout.isatty()

    threshold1 = args.threshold1
    threshold2 = args.threshold2

    ping(args.host, args.count, args.interval, args.size)
