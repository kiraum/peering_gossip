# peering_gossip

![pylint](https://github.com/kiraum/peering_gossip/actions/workflows/pylint.yml/badge.svg)
![CodeQL](https://github.com/kiraum/peering_gossip/actions/workflows/github-code-scanning/codeql/badge.svg)
[![Generate IXPs reports](https://github.com/kiraum/peering_gossip/actions/workflows/generate_reports.yml/badge.svg)](https://github.com/kiraum/peering_gossip/actions/workflows/generate_reports.yml)

The idea is to have a gossip tool generating a Hall of Shame for Autonomous Systems that are not so polite.

**Reports are being automatically generated and committed daily to this repository.**

```
% python3 peering_gossip.py -h
usage: peering_gossip.py [-h] [-lg ALICE_URL] [-a]

Peering Gossip - Gossiping about bad practices!

optional arguments:
  -h, --help     show this help message and exit
  -lg ALICE_URL  Check Alice looking glass for top filtered ASNs, and generates a report.
  -a             Generate report for all ixps from pgossip/config.yaml.
```

### daily reports
- [IX.br](reports/lg.ix.br.txt)
- [IX.br json](reports/lg.ix.br.json)
- [DE-CIX](reports/lg.de-cix.net.txt)
- [DE-CIX json](reports/lg.de-cix.net.json)
- [AMS-IX](reports/lg.ams-ix.net.txt)
- [AMS-IX json](reports/lg.ams-ix.net.json)
- [LINX](reports/alice-rs.linx.net.txt)
- [LINX json](reports/alice-rs.linx.net.json)

### install
```
% git clone git@github.com:kiraum/peering_gossip.git
% python3 -m venv venv
% . venv/bin/activate
% pip install --no-cache-dir -U pip uv
% uv pip install -r requirements.txt
```

### use it
```
% . venv/bin/activate
% python3 peering_gossip.py -lg https://lg.ams-ix.net
```

### example usage
to run agains one looking glass:
```
% python3 peering_gossip.py -lg https://lg.ams-ix.net
Working on https://lg.ams-ix.net - nl-rc-v4
Working on https://lg.ams-ix.net - nl-rc-v6
Working on https://lg.ams-ix.net - hk-rs1-v4
Working on https://lg.ams-ix.net - hk-rs1-v6
Working on https://lg.ams-ix.net - hk-rs2-v4
Working on https://lg.ams-ix.net - hk-rs2-v6
Working on https://lg.ams-ix.net - cw-rs1-v4
Working on https://lg.ams-ix.net - cw-rs1-v6
Working on https://lg.ams-ix.net - cw-rs2-v4
Working on https://lg.ams-ix.net - cw-rs2-v6
Working on https://lg.ams-ix.net - mum-rs1-v4
Working on https://lg.ams-ix.net - mum-rs1-v6
Working on https://lg.ams-ix.net - mum-rs2-v4
Working on https://lg.ams-ix.net - mum-rs2-v6
Working on https://lg.ams-ix.net - chi-rs1-v4
Working on https://lg.ams-ix.net - chi-rs1-v6
Working on https://lg.ams-ix.net - chi-rs2-v4
Working on https://lg.ams-ix.net - chi-rs2-v6
Working on https://lg.ams-ix.net - ba-rs1-v4
Working on https://lg.ams-ix.net - ba-rs1-v6
Working on https://lg.ams-ix.net - ba-rs2-v4
Working on https://lg.ams-ix.net - ba-rs2-v6
Filtered prefixes @ https://lg.ams-ix.net | ASN | AS-NAME | AS Rank | Source | Country | PeeringDB link
1634 | 7713 | TELKOMNET-AS-AP PT Telekomunikasi Indonesia | 69 | APNIC | ID | https://www.peeringdb.com/asn/7713
198 | 134548 | DXTL-HK DXTL Tseung Kwan O Service | 2833 | APNIC | HK | https://www.peeringdb.com/asn/134548
144 | 24429 | TAOBAO Zhejiang Taobao Network Co. | 2666 | APNIC | US | https://www.peeringdb.com/asn/24429
28 | 18229 | CTRLS-AS-IN CtrlS | 294 | APNIC | IN | https://www.peeringdb.com/asn/18229
8 | 6939 | HURRICANE | 6 | ARIN | US | https://www.peeringdb.com/asn/6939
8 | 199524 | GCORE - G-Core Labs S.A. | 345 | RIPE | LU | https://www.peeringdb.com/asn/199524
8 | 9583 | SIFY-AS-IN Sify Limited | 97 | APNIC | IN | https://www.peeringdb.com/asn/9583
7 | 58779 | I4HKLIMITED-AS i4HK Limited | 2190 | APNIC | HK | https://www.peeringdb.com/asn/58779
4 | 9304 | HUTCHISON-AS-AP HGC Global Communications Limited | 86 | APNIC | HK | https://www.peeringdb.com/asn/9304
4 | 136334 | VNPL-AS Vortex Netsol Private Limited | 694 | APNIC | IN | https://www.peeringdb.com/asn/136334
2 | 7552 | VIETEL-AS-AP Viettel Group | 219 | APNIC | VN | https://www.peeringdb.com/asn/7552
2 | 64567 | AMS-IX | NA | NA | NL | https://www.peeringdb.com/asn/64567
2 | 36351 | SOFTLAYER | 1921 | ARIN | US | https://www.peeringdb.com/asn/36351
2 | 55352 | MCPL-IN Microscan Infocommtech Private Limited | 677 | APNIC | IN | https://www.peeringdb.com/asn/55352
2 | 132770 | GAZON-AS-IN Gazon Communications India Limited | 467 | APNIC | IN | https://www.peeringdb.com/asn/132770
================================================================================
We created a sharable report link, enjoy => https://glot.io/snippets/gw9fx0fc4a
```

or to run againt all ASNs from config.yaml:
```
% python3 peering_gossip.py -a
...
```
