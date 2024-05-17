""" Peering Gossip """

import json
import os
import sys
import time

import backoff
import requests
import yaml


class RetryMeta(type):
    """
    A metaclass that applies retry logic to all callable methods of a class using backoff.

    This metaclass enhances methods to retry up to 5 times upon `requests.exceptions.RequestException`,
    using an exponential backoff strategy. It automatically decorates all methods that are not special
    methods (not starting with '__').

    Attributes:
        name (str): The name of the class.
        bases (tuple): The base classes of the class.
        dct (dict): The dictionary containing the class's attributes.

    Returns:
        type: The new class with modified methods.
    """

    def __new__(mcs, name, bases, dct):
        for key, value in dct.items():
            if callable(value) and not key.startswith("__"):
                dct[key] = backoff.on_exception(
                    backoff.expo, requests.exceptions.RequestException, max_tries=5
                )(value)
        return type.__new__(mcs, name, bases, dct)


class PGossip(metaclass=RetryMeta):
    """
    A class to handle peering and routing information gathering and reporting.

    This class provides methods to fetch and analyze routing data from specified URLs,
    generate reports based on the gathered data, and manage interactions with external APIs
    for data retrieval and report generation.

    Methods:
        alice_host(url): Main method to process routing data for a given URL.
        parse_text_to_json(data_text): Converts text data into JSON format.
        write_report_to_file(fname, data, as_json): Writes data to a file in text or JSON format.
        alice_rs(url): Fetches alive route servers from a given URL.
        alice_neighbours(url, route_server): Fetches routing neighbors for a specific route server.
        bv_asn_whois(asn): Retrieves ASN WHOIS information from the BGPView API.
        create_report(data): Creates a pastebin-like report.
        load_yaml(): Loads a YAML configuration file.

    Attributes:
        None explicitly defined; configuration and state are managed internally within methods.
    """

    def __init__(self):
        pass

    # pylint: disable=too-many-locals
    def alice_host(self, url):
        """
        Generate hall of shame based on provided URL.

        Args:
            url (str): The URL to fetch data from.

        Returns:
            None
        """
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
            # AMS-IX using private ASN :(
            if asn != 64567:
                details = self.bv_asn_whois(asn)
                time.sleep(0.5)
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
        self.write_report_to_file(fname, "\n".join(map(str, text)), as_json=False)
        self.write_report_to_file(fname, "\n".join(map(str, text)), as_json=True)

    def parse_text_to_json(self, data_text):
        """
        Convert a list of delimited text data into a list of dictionaries.

        Args:
            data_text (str): A string containing multiple lines of data, each line is a delimited record.

        Returns:
            list: A list of dictionaries with parsed data.
        """
        lines = data_text.strip().split("\n")
        headers = [header.strip() for header in lines[0].split("|")]
        json_data = []

        for line in lines[1:]:
            values = [value.strip() for value in line.split("|")]
            entry = dict(zip(headers, values))
            json_data.append(entry)
        return json_data

    def write_report_to_file(self, fname: str, data: list, as_json: bool = False):
        """
        Write data to a file, creating the necessary directories if they do not exist.
        The data can be written as plain text or as JSON.

        Args:
            fname (str): The filename (without extension) where the data will be saved.
            data (list): A list of data entries, each entry can be a string or a dictionary.
            as_json (bool): If True, writes the data in JSON format. Otherwise, writes as plain text.

        Example:
            write_report_to_file("2023-01-01_report", data, as_json=True)
        """
        # Construct the full file path with directory and filename
        extension = "json" if as_json else "txt"
        fwrite = f"reports/{fname}.{extension}"

        # Ensure the directory exists; if not, create it
        os.makedirs(os.path.dirname(fwrite), exist_ok=True)

        # Open the file and write the data to it
        with open(fwrite, "w", encoding="utf8") as tfile:
            if as_json:
                data = self.parse_text_to_json(data)
                json.dump(data, tfile, indent=4)
            else:
                tfile.write(data)

    def alice_rs(self, url):
        """
        Get alive looking glass route servers.

        Args:
            url (str): The base URL.

        Returns:
            list: List of alive route servers.
        """
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
        """
        Get alive looking glass neighbors for a specific route server.

        Args:
            url (str): The base URL.
            route_server (str): The ID of the route server.

        Returns:
            dict: Dictionary containing neighbor ASNs and their filtered routes.
        """
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
        """
        Return ASN whois information from BGPView API.

        Args:
            asn (int): The ASN to retrieve information for.

        Returns:
            dict: Dictionary containing ASN whois information.
        """
        url = f"https://api.bgpview.io/asn/{asn}"
        result = None
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
            print(
                "ERROR | HTTP status != 200 - bv_asn_whois"
                f" - Error {response.status_code}: {asn}"
            )
            sys.exit(1)
        return result

    def create_report(self, data):
        """
        Create a pastebin-like report using glot.io API.

        Args:
            data (str): The data to include in the report.

        Returns:
            str: URL of the created report.
        """
        url = "https://glot.io/api/snippets"
        report_url = None
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
        """
        Load a YAML config file.

        Returns:
            dict: Dictionary containing the YAML config data.
        """
        with open("pgossip/config.yaml", "r", encoding="utf8") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        return data
