# python-ping

Ping using python raw socket
---

```
usage: sudo ping.py [-h] [--version] [-c COUNT] [-t TTL] [-s PACKETSIZE]
               [--timeout TIMEOUT]
               host

positional arguments:
  host               Target host

optional arguments:
  -h, --help         Show help message and exit
  --version          Show program's version number and exit
  -c COUNT           Send count ECHO_REQUEST packets (default:3)
  -t TTL             Set the IP Time to Live (default:64)
  -s PACKETSIZE      Set the sending packet size (default:64)
  --timeout TIMEOUT  Set the timeout (default: 2s)

```

> Notice: Running as root.

---

Author: Medici.Yan

Site: http://blog.evalbug.com