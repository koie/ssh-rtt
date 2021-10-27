#!/usr/bin/env python3

import argparse
import datetime
import itertools
import math
import random
import subprocess
import sys
import time

ssh_cmd = ["ssh"]
cat_cmd = ["cat"]

coloring = True
threshold1 = "> avg + std"
threshold2 = "> avg + 2 * std"


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
        if self.n == 0:
            return None
        return self.s / self.n

    def var(self):
        return self.m / (self.n - 1) if self.n > 1 else 0

    def stddev(self):
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

    def decorate(text, color):
        if color == Color.END:
            return text
        else:
            return color + text + Color.END


def gen_nonce(size):
    nonce = ""
    while len(nonce) < size:
        nonce = nonce + str(random.randint(0, 99999999))
    nonce = nonce[:size] + "\n"
    return nonce.encode()


def ping(ssh_arg, n, wait, size):
    hostname = " ".join(ssh_arg)
    print(f"PING {hostname}", flush=True)
    args = ssh_cmd + ssh_arg + cat_cmd
    with subprocess.Popen(args=args,
                          shell=False,
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          bufsize=0) as proc:
        vs = VarState()
        for i in (range(n+1) if n > 0 else itertools.count(0)):
            if i > 0:
                time.sleep(wait)
            nonce = gen_nonce(size)
            start = time.clock_gettime(time.CLOCK_REALTIME)
            proc.stdin.write(nonce)
            while True:
                nonce2 = proc.stdout.readline()
                if nonce2 == nonce:
                    break
                print(f"unexpected response: {nonce2}", flush=True)
            end = time.clock_gettime(time.CLOCK_REALTIME)
            rtt = end - start

            color = Color.END
            if coloring and i >= 10:
                if local_eval("rtt " + threshold2,
                              i, rtt, vs.min, vs.avg(), vs.max, vs.stddev()):
                    color = Color.RED
                elif local_eval("rtt " + threshold1,
                                i, rtt, vs.min, vs.avg(), vs.max, vs.stddev()):
                    color = Color.YELLOW

            if i > 0:  # because first rtt may be slow, discard it.
                vs.update(rtt)

            output(color, start, i, rtt, vs.min, vs.avg(), vs.max, vs.stddev())


def local_eval(expr, i, rtt, min, avg, max, std):
    return eval(expr)


def output(color, now, i, rtt, min, avg, max, std):
    output = str(datetime.datetime.fromtimestamp(now))
    output += f", seq={i} "
    output += Color.decorate(f"time={rtt*1000:.3f} ms", color)
    if i > 0:
        output += f", min={min*1000:.3f} ms"
        output += f", avg={avg*1000:.3f} ms"
        output += f", max={max*1000:.3f} ms"
        if i > 1:
            output += f", std={std*1000:.3f} ms"
    print(output, flush=True)


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

    try:
        ping(args.host, args.count, args.interval, args.size)
    except KeyboardInterrupt:
        pass
