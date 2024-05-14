# peering_gossip

![pylint](https://github.com/kiraum/peering_gossip/actions/workflows/pylint.yml/badge.svg)
![CodeQL](https://github.com/kiraum/peering_gossip/actions/workflows/github-code-scanning/codeql/badge.svg)

The idea is to have a gossip tool generating a Hall of Shame for Autonomous Systems that are not so polite.

**Reports are being automatically generated and committed daily (or weekly, not clear yet) to this repository.**

```
% ./peering_gossip.py -h
usage: peering_gossip.py [-h] [-lg ALICE_URL] [-a]

Peering Gossip - Gossiping about bad practices!

optional arguments:
  -h, --help     show this help message and exit
  -lg ALICE_URL  Check Alice looking glass for top filtered ASNs, and generates a report.
  -a             Generate report for all ixps from pgossip/config.yaml.
```

### example reports
- [IX.br](reports/lg.ix.br.txt)
- [DE-CIX](reports/lg.de-cix.net.txt)
- [AMS-IX](reports/lg.ams-ix.net.txt)
- [LINX](reports/alice-rs.linx.net.txt)

### install
```
git clone git@github.com:kiraum/peering_gossip.git
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

### use it
```
% . venv/bin/activate
% pbuddy/pbuddy.py
```

### example usage
```
% ./peering_gossip.py -lg https://alice-rs.linx.net
rs1-in2-lon1-linx-net-v4
rs1-in2-lon1-linx-net-v6
rs3-tch-lon1-linx-net-v4
rs3-tch-lon1-linx-net-v6
rs2-in2-lon2-linx-net-v4
rs2-in2-lon2-linx-net-v6
rs1-tcw-man1-linx-net-v4
rs1-tcw-man1-linx-net-v6
rs1-pue-sco1-linx-net-v4
rs1-pue-sco1-linx-net-v6
rs1-ngd-car1-linx-net-v4
rs1-ngd-car1-linx-net-v6
rs1-imm-nva1-linx-net-v4
rs1-imm-nva1-linx-net-v6
rs2-dft-nva1-linx-net-v4
rs2-dft-nva1-linx-net-v6
rs2-dvg-sco1-linx-net-v4
rs2-dvg-sco1-linx-net-v6
rs2-bts-car1-linx-net-v4
rs2-bts-car1-linx-net-v6
rs4-tch-lon2-u22-linx-net-v4
rs4-tch-lon2-u22-linx-net-v6
rs2-tcj-man1-linx-net-v4
rs2-tcj-man1-linx-net-v6
Filtered prefixes @ https://alice-rs.linx.net | ASN | NAME | Contacts | PeeringDB link
3066 | 3216 | SOVAM-AS | abuse-b2b@beeline.ru,peering@beeline.ru,wholesale@beeline.ru,noc@sovintel.ru,noc@beeline.ru | https://www.peeringdb.com/asn/3216
1182 | 39386 | STC-IGW-AS | registry@stc.com.sa,araiyes@stc.com.sa,registry@saudi.net.sa | https://www.peeringdb.com/asn/39386
783 | 7713 | telkomnet-as-ap | abuse@telkom.co.id,peering@telin.net,yogo@telkom.co.id,torkis@telin.net | https://www.peeringdb.com/asn/7713
546 | 57463 | NetIX | abuse@netix.net,nmt@netix.net | https://www.peeringdb.com/asn/57463
...
2 | 59624 | KIAE-COMPUTING-AS | ip-box@ripn.net,noc@kiae.ru,noc@computing.kiae.ru,andssh@gmail.com | https://www.peeringdb.com/asn/59624
2 | 60171 | AFRIX-AS | noc@afr-ix.com,engineering@afr-ix.com,nalbi@afr-ix.com | https://www.peeringdb.com/asn/60171
2 | 61955 | ColocationIX-AS | colocationix.abuse@colocationix.net,hostmaster@consultix.net,hostmaster@colocationix.net | https://www.peeringdb.com/asn/61955
2 | 396998 | PATH-NETWORK | abuse@path.net,noc@path.net | https://www.peeringdb.com/asn/396998
2 | 3741 | None |  | https://www.peeringdb.com/asn/3741
2 | 6894 | KDDI-EUROPE | ipdata@uk.kddi.eu,nameadmin@kew.net | https://www.peeringdb.com/asn/6894
1 | 3225 | Gulfnet-Kuwait | noc@bonline.com.kw,a.elmirghany@bonline.com.kw,it.core@bonline.com.kw,core@bonline.com.kw | https://www.peeringdb.com/asn/3225
1 | 20940 | AKAMAI-ASN1 | abuse@akamai.com,ip-admin@akamai.com,ck@akamai.com,nbakker@akamai.com,ripenotify@bakker.net,rmullall@akamai.com,registry@4l.ie,cdabanog@akamai.com | https://www.peeringdb.com/asn/20940
1 | 29129 | VISPA-ASN | ripe@vispa.net,james@vispa.net | https://www.peeringdb.com/asn/29129
================================================================================
We created a sharable report link, enjoy => https://glot.io/snippets/glqb1ka3j8

```
