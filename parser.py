#!/usr/bin/env python3
# parser.py app for parsing xml files

import xml.etree.ElementTree as ET, os
from datetime import datetime, timedelta

# Folder with all xml files
FOLDER_PATH = "testinputs"

# This function converts start date and bitmapdays
# To a list of valid dates
def cal_to_listofdays(calendar):
    binstr = calendar['BitmapDays']
    startdate = calendar['ValidityPeriod']['StartDateTime']
    startdate = startdate[:startdate.rfind('T'):]
    ret = []
    start = datetime.strptime(startdate, "%Y-%m-%d")
    for i in range(len(binstr)):
        if binstr[i] == '1':
            ret.append(str(start + timedelta(days=i))[:10:])
    return ret

# Recursively gathers all data from a node
# and converts it to a dict
def node_to_dict(node, ignore=[]):
    ND = {}
    if(len(node) == 0):
        return node.text
    for child in node:
        if child.tag in ignore:
            continue
        if child.tag not in ND:
            ND[child.tag] = node_to_dict(child)
        else:
            if type(ND[child.tag]) is list:
                ND[child.tag].append(node_to_dict(child))
            else:
                ND[child.tag] = [ND[child.tag]] + [node_to_dict(child)]
    return ND

# Create a generator object returning xml files with data
# folder_path: path to folder containing xml files for parsing
def xml_file_generator():
    for root, _, files in os.walk(FOLDER_PATH):
        for file in files:
            if(file.endswith(".xml")):
                yield os.path.join(root, file)

# Creates a generator returning a dictionary with parsed data
def parsed_data_generator():
    for file in xml_file_generator():
        yield parse_file(file)

# Parses single file from arguments, returns a dict of parsed data
def parse_file(file):
    # XML tree
    tree = ET.parse(file)
    root = tree.getroot()

    # Dict with parsed info init
    DT = {}

    # Name of the data origin file
    DT["filename"] = os.path.basename(file)

    # Type of file - normal or cancel
    DT["type"] = "cancel" if "cancel" in DT["filename"] else "normal"

    # All identifiers
    DT["ids"] = [node_to_dict(x) for x in root.findall(".//PlannedTransportIdentifiers")]

    # Raw info about valid days
    DT["calendar"] = node_to_dict(root.find(".//PlannedCalendar"))

    # Same as "calendar" but its parsed to a list of valid days format YYYY-MM-DD
    DT["list_calendar"] = cal_to_listofdays(DT['calendar'])
    
    # In cancelation file no more data is found
    if DT["type"] == "cancel":
        # Time of cancelation
        DT["canceled"] = root.find(".//CZPTTCancelation").text
        return DT

    # List of train stop info (0ty prvek je vychozi stanice, posledni je cilova stanice)
    DT["locations"] = []

    # List of timings at each locacion (0ty prvek je vychozi stanice, posledni je cilova stanice)
    # Vychozi a cilova stanice maji jen jeden cas - vychozi odjezd, cilova prijezd
    # Stanice mezi nimi maji casy oba
    DT["timings"] = []

    # Network info (not used in this project)
    DT["network"] = []

    # Time of creation of the file
    DT["creation"] = root.find(".//CZPTTCreation").text

    # Additional info at each location (0ty prvek je vychozi stanice, posledni je cilova stanice)
    DT["at_loc_info"] = []

    # Parsing
    for location in root.findall(".//Location"):
        DT["locations"].append(node_to_dict(location))
    for timing in root.findall(".//TimingAtLocation"):
        DT["timings"].append(node_to_dict(timing))
    for network in root.findall("./NetworkSpecificParameter"):
        DT["network"].append(node_to_dict(network))
    for info in root.findall(".//CZPTTLocation"):
        DT["at_loc_info"].append(node_to_dict(info, ["Location", "TimingAtLocation"]))
    return DT

# Tohle je demo ktere ukazuje jak vypadaji zparsovana data ve vnitrni
# reprezentaci pythonu.
# ocekavaji se vstupni .xml soubory ve slozce urcene glob. promennou FOLDER_PATH
def main():
    filecount = 0
    print("*************************************************")
    for parsed in parsed_data_generator(): # Each loop iteration means one file parsed.
        filecount += 1
        if parsed["type"] == "normal":
            print(f'filename: {parsed["filename"]}')
            print(f'ids: {parsed["ids"]}')
            print(f'Vychozi stanice: {parsed["locations"][0]}\n  {parsed["timings"][0]}\n  {parsed["at_loc_info"][0]}\n')
            print(f'Cilova stanice:  {parsed["locations"][-1]}\n  {parsed["timings"][-1]}\n  {parsed["at_loc_info"][-1]}\n')
            print(f'Kalenar: {parsed["calendar"]}\n')
            print(f'Kalendar v listu: {parsed["list_calendar"]}')
            print(f'Creation: {parsed["creation"]}')
            print(f'Network: {parsed["network"]}')
        else: # Canceled type
            print(f'filename: {parsed["filename"]}')
            print(f'ids: {parsed["ids"]}')
            print(f'Kalenar: {parsed["calendar"]}\n')
            print(f'Kalendar v listu: {parsed["list_calendar"]}')
            print(f'Canceled: {parsed["canceled"]}')
        print(f"************************************************* {filecount} ***************")
    print(f"Parsed {filecount} files.")

if __name__ == '__main__':
    main()