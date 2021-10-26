# `ssh-rtt` - ping over SSH

## Usage

```
% chmod +x ssh-rtt.py
% ./ssh-rtt.py -h
usage: ssh-rtt.py [-h] [-c COUNT] [-i WAIT] [-s SIZE] [--color] [--no-color]
                  [--threshold1 THRESHOLD1] [--threshold2 THRESHOLD2]
                  HOST [HOST ...]

Ping over SSH

positional arguments:
  HOST

optional arguments:
  -h, --help            show this help message and exit
  -c COUNT, --count COUNT
  -i WAIT, --interval WAIT
  -s SIZE, --size SIZE
  --color
  --no-color
  --threshold1 THRESHOLD1
  --threshold2 THRESHOLD2
% ./ssh-rtt.py -i 0.3 -- -v localhost
PING -v localhost
...
seq=0 time=281.975 ms
seq=1 time=0.345 ms, min=0.345 ms, avg=0.345 ms, max=0.345 ms, std=0.000 ms
seq=2 time=0.306 ms, min=0.306 ms, avg=0.326 ms, max=0.345 ms, std=0.028 ms
seq=3 time=0.426 ms, min=0.306 ms, avg=0.359 ms, max=0.426 ms, std=0.061 ms
seq=4 time=0.323 ms, min=0.306 ms, avg=0.350 ms, max=0.426 ms, std=0.053 ms
seq=5 time=0.355 ms, min=0.306 ms, avg=0.351 ms, max=0.426 ms, std=0.046 ms
seq=6 time=0.284 ms, min=0.284 ms, avg=0.340 ms, max=0.426 ms, std=0.050 ms
seq=7 time=0.283 ms, min=0.283 ms, avg=0.332 ms, max=0.426 ms, std=0.050 ms
seq=8 time=0.360 ms, min=0.283 ms, avg=0.335 ms, max=0.426 ms, std=0.047 ms
seq=9 time=0.288 ms, min=0.283 ms, avg=0.330 ms, max=0.426 ms, std=0.047 ms
seq=10 time=0.272 ms, min=0.272 ms, avg=0.324 ms, max=0.426 ms, std=0.048 ms
```

