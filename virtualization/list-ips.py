# This script accepts one argument - number of IPs to be listed

import ipaddress
import sys


def main(args):
    max_ips = int(args[0])
    excluded_ips = ["172.18.0.0", "172.18.0.1"]

    ips_created = 0
    for ip in ipaddress.IPv4Network("172.18.0.0/16"):
        if ips_created == max_ips:
            break
        ip_str = str(ip)
        if ip_str not in excluded_ips:
            ips_created += 1
            print(ip_str)


if __name__ == "__main__":
    main(sys.argv[1:])
