# peering_gossip

The idea is to have a gossip tool generating a Hall of Shame for Autonomous Systems that are not so polite.

```
% ./peering_gossip.py
usage: peering_gossip.py [-h] [-lg ALICE_URL]

Peering Gossip - Gossiping about bad practices!

optional arguments:
  -h, --help     show this help message and exit
  -lg ALICE_URL  Check Alice looking glass for top filtered ASNs, and generates a report.
```

### example reports
- [IX.br](reports/ixbr)
- [DE-CIX](reports/decix) 
- [AMS-IX](reports/amsix)
- [LINX](reports/linx)

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