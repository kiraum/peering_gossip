""" Peering Gossip """
import sys
import json
import time
import yaml
import requests


class PGossip:
    """
    Peering Buddy class
    """

    # pylint: disable=too-many-locals
    def alice_hos(self, url):
        """generate hall of shame"""
        filtered_routes_sorted = None
        filtered_routes_clean = None
        filtered_routes_sum = {}
        text = []
        fname = url.replace("https://", "")
        rs_list = self.alice_rs(url)
        for route_server in rs_list:
            print(f"Working on {url} - {route_server}")
            filtered_routes = self.alice_neighbours(url, route_server)
            if filtered_routes is None:
                continue

            for neighbour, froutes in filtered_routes.items():
                if neighbour in filtered_routes_sum:
                    filtered_routes_sum[neighbour] = (
                        filtered_routes_sum[neighbour] + froutes
                    )
                else:
                    filtered_routes_sum[neighbour] = froutes
            time.sleep(60)

        filtered_routes_sorted = dict(
            sorted(filtered_routes_sum.items(), key=lambda item: item[1], reverse=True)
        )
        filtered_routes_clean = {
            x: y for x, y in filtered_routes_sorted.items() if y != 0
        }

        text.append(
            f"Filtered prefixes @ {url} | ASN | NAME | Contacts | PeeringDB link"
        )
        for asn, pfxs in filtered_routes_clean.items():
            if asn != 64567:
                details = self.bv_asn_whois(asn)
            else:
                details["name"] = "Private ASN"
                details["email_contacts"] = ["noc@mas-ix.net"]
            text.append(
                f"{pfxs} | {asn} | {details['name']} "
                f"| {','.join(map(str, details['email_contacts']))} "
                f"| https://www.peeringdb.com/asn/{asn}"
            )
        print("\n".join(map(str, text)))
        report_link = self.create_report("\n".join(map(str, text)))
        print("=" * 80)
        print(f"We created a sharable report link, enjoy => {report_link}")
        fwrite = f"reports/{fname}"
        with open(fwrite, "w", encoding="utf8") as tfile:
            tfile.write("\n".join(map(str, text)))

    def alice_rs(self, url):
        """get alive lg rs"""
        url = f"{url}/api/v1/routeservers"
        with requests.Session() as session:
            response = session.get(url)
        if response.status_code == 200:
            rs_list = []
            data = json.loads(response.text)
            for rserver in data["routeservers"]:
                rs_list.append(rserver["id"])
        else:
            print("ERROR | HTTP status != 200 - alice_rs")
            sys.exit(1)
        return rs_list

    def alice_neighbours(self, url, route_server):
        """get alive lg neighbors"""
        url = f"{url}/api/v1/routeservers/{route_server}/neighbors"
        with requests.Session() as session:
            response = session.get(url)
        if response.status_code == 200:
            neighbour_dict = {}
            data = json.loads(response.text)
            if "neighbors" in data:
                neigh = "neighbors"
            else:
                neigh = "neighbours"
            for neighbour in data[neigh]:
                if neighbour["asn"] in neighbour_dict:
                    neighbour_dict[neighbour["asn"]] = (
                        neighbour_dict[neighbour["asn"]] + neighbour["routes_filtered"]
                    )
                else:
                    neighbour_dict[neighbour["asn"]] = neighbour["routes_filtered"]
        else:
            print(
                "ERROR | HTTP status != 200 - alice_neighbours"
                f" - Error {response.status_code}: {url} - {route_server}"
            )
            if response.status_code == 500:
                neighbour_dict = None
        return neighbour_dict

    def bv_asn_whois(self, asn):
        """return asn whois information"""
        url = f"https://api.bgpview.io/asn/{asn}"
        with requests.Session() as session:
            response = session.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            try:
                result = data["data"]
            except KeyError:
                print(f"ASN {asn} has no data at whois!")
                raise
        else:
            print("ERROR | HTTP status != 20 - bv_asn_whois")
            sys.exit(1)
        return result

    def create_report(self, data):
        """create a pastebin like report"""
        url = "https://glot.io/api/snippets"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        payload = {
            "language": "plaintext",
            "title": "Report",
            "public": True,
            "files": [{"name": "report.txt", "content": data}],
        }

        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            report_url = f"https://glot.io/snippets/{response.json()['id']}"
        else:
            print("ERROR | HTTP status != 200 - create_report")
            sys.exit(1)
        return report_url

    def load_yaml(self):
        """load yaml config file"""
        with open("pgossip/config.yaml", "r", encoding="utf8") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        return data
