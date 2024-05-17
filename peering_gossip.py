#!/usr/bin/env python3
"""
Peering Gossip - Gossiping about bad practices!
"""

import argparse
import asyncio
import sys

from pgossip.pgossip import PGossip


async def main():
    """Peering Gossip"""
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

    if args.lg:
        await pgossip.alice_host(args.lg)

    if args.all:
        ixps = pgossip.load_yaml()
        await pgossip.process_all_ixps_concurrently(ixps)

    if not options:
        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
