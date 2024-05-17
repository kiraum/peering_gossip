""" Peering Gossip """

import asyncio
import json
import os
import sys

import aiohttp
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

    async def alice_host(self, url):
        """
        Asynchronously generates a report based on route server data from a specified URL.

        This method orchestrates the fetching of route server data, processes each server concurrently,
        sorts and filters the results, and finally compiles a detailed report which includes ASN details.

        Args:
            url (str): The base URL from which to fetch route server data.

        Processes:
            1. Fetches a list of route servers.
            2. Concurrently processes each route server to accumulate route data.
            3. Sorts and filters the accumulated data.
            4. Concurrently fetches detailed ASN information.
            5. Compiles and prints a detailed report, and saves it both as text and JSON.

        Outputs:
            Prints the compiled report and creates a shareable report link.
            Saves the report to a file in both plain text and JSON format.
        """
        filtered_routes_sum = {}
        text = []
        fname = url.replace("https://", "")
        rs_list = await self.alice_rs(url)

        tasks = [
            self.process_route_server(url, rs, filtered_routes_sum) for rs in rs_list
        ]
        await asyncio.gather(*tasks)

        filtered_routes_sorted = dict(
            sorted(filtered_routes_sum.items(), key=lambda item: item[1], reverse=True)
        )
        filtered_routes_clean = {
            x: y for x, y in filtered_routes_sorted.items() if y != 0
        }

        text.append(
            f"Filtered prefixes @ {url} | ASN | AS-NAME | AS Rank | Source | Country | PeeringDB link"
        )

        asn_details_tasks = [
            self.get_asn_details(asn, pfxs)
            for asn, pfxs in filtered_routes_clean.items()
        ]
        asn_details = await asyncio.gather(*asn_details_tasks)

        for detail in asn_details:
            text.append(detail)

        print("\n".join(map(str, text)))
        report_link = await self.create_report("\n".join(map(str, text)))
        print("=" * 80)
        print(f"We created a sharable report link, enjoy => {report_link}")
        await self.write_report_to_file(fname, "\n".join(map(str, text)), as_json=False)
        await self.write_report_to_file(fname, "\n".join(map(str, text)), as_json=True)

    async def process_route_server(self, url, route_server, filtered_routes_sum):
        """
        Processes a route server asynchronously and updates the route summaries.

        Args:
            url (str): Base URL for route server data.
            route_server (str): Identifier for the route server.
            filtered_routes_sum (dict): Dictionary to accumulate route data.

        This method fetches route data, updates the summary dictionary, and includes a delay to manage API calls.
        """
        print(f"Working on {url} - {route_server}")
        filtered_routes = await self.alice_neighbours(url, route_server)
        if filtered_routes is None:
            return

        for neighbour, froutes in filtered_routes.items():
            if neighbour in filtered_routes_sum:
                filtered_routes_sum[neighbour] += froutes
            else:
                filtered_routes_sum[neighbour] = froutes
        await asyncio.sleep(60)  # Non-blocking sleep

    async def get_asn_details(self, asn, pfxs):
        """
        Asynchronously retrieves and formats ASN details for display.

        This method handles special cases for private ASNs and includes a delay to manage API rate limits.

        Args:
            asn (int): The Autonomous System Number to query.
            pfxs (int): The number of prefixes associated with the ASN.

        Returns:
            str: A formatted string with ASN details and a PeeringDB link.

        Note:
            Assumes `caida_asn_whois` fetches ASN details and `asyncio.sleep` is used to avoid rate limits.
        """
        if asn != 64567:  # AMS-IX using private ASN
            details = await self.caida_asn_whois(asn)
            await asyncio.sleep(0.5)  # Non-blocking sleep
        else:
            details = {
                "asnName": "Private ASN",
                "rank": "NA",
                "source": "NA",
                "country": {"iso": "NL"},
            }

        if details:
            if not details.get("asnName"):
                details["asnName"] = "NA"
        else:
            details = {
                "asnName": "NA",
                "rank": "NA",
                "source": "NA",
                "country": {"iso": "NA"},
            }

        return (
            f"{pfxs} | {asn} | {details['asnName']} | {details['rank']} | {details['source']} | {details['country']['iso']} "
            f"| https://www.peeringdb.com/asn/{asn}"
        )

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

    async def write_report_to_file(self, fname: str, data: list, as_json: bool = False):
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
        extension = "json" if as_json else "txt"
        fwrite = f"reports/{fname}.{extension}"

        os.makedirs(os.path.dirname(fwrite), exist_ok=True)

        with open(fwrite, "w", encoding="utf8") as tfile:
            if as_json:
                data = self.parse_text_to_json(data)
                json.dump(data, tfile, indent=4)
            else:
                tfile.write(data)

    async def alice_rs(self, url):
        """
        Get alive looking glass route servers.

        Args:
            url (str): The base URL.

        Returns:
            list: List of alive route servers.
        """
        url = f"{url}/api/v1/routeservers"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    rs_list = []
                    data = await response.json()
                    for rserver in data["routeservers"]:
                        rs_list.append(rserver["id"])
                else:
                    print("ERROR | HTTP status != 200 - alice_rs")
                    sys.exit(1)
        return rs_list

    async def alice_neighbours(self, url, route_server):
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
                f" - Error {response.status_code}: {asn} => {response.reason}"
            )
            sys.exit(1)
        return result

    async def caida_asn_whois(self, asn):
        """
        Fetches WHOIS information for a specified ASN from the CAIDA AS Rank API.

        Args:
            asn (int): The Autonomous System Number to query.

        Returns:
            dict: WHOIS information if the request is successful, None otherwise.

        Raises:
            KeyError: If expected data keys are missing in the response.
            SystemExit: If the API response is not successful (non-200 status code).
        """
        url = f"https://api.asrank.caida.org/v2/restful/asns/{asn}"
        result = None
        with requests.Session() as session:
            response = session.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            try:
                result = data["data"]["asn"]
            except KeyError:
                print(f"ASN {asn} has no data at whois!")
                raise
        else:
            print(
                "ERROR | HTTP status != 200 - caida_asn_whois"
                f" - Error {response.status_code}: {asn} => {response.reason}"
            )
            sys.exit(1)
        return result

    async def create_report(self, data):
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
