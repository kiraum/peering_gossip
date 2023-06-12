#!/usr/bin/env python3
"""
Peering Gossip - Gossiping about bad practices!
"""

import sys
import argparse

from pgossip.pgossip import PGossip


def main():
    """Peering Gossip main"""
    parser = argparse.ArgumentParser(
        description="Peering Gossip - Gossiping about bad practices!"
    )
    parser.add_argument(
        "-lg",
        action="store",
        dest="lg",
        metavar="ALICE_URL",
        help="Check Alice looking glass for top filtered ASNs, and generates a report.",
    )
    parser.add_argument(
        "-a",
        action="store_true",
        dest="all",
        help="Generate report for all ixps from pgossip/config.yaml.",
    )

    args = parser.parse_args()
    options = all(value is True for value in vars(args).values())

    pgossip = PGossip()

    if args.lg is not None:
        pgossip.alice_hos(args.lg)

    if args.all is True:
        ixps = pgossip.load_yaml()
        for ixp in ixps["ixps"]:
            pgossip.alice_hos(ixp)
    
    print(args)

    if options is False:
        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
