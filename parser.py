#!/usr/bin/env python3
# parser.py app for parsing xml files

import xml.etree.ElementTree as ET, os

# Folder with all xml files
FOLDER_PATH = "testinputs"

# Recursively gathers all data from a node
# and converts it to a dict
def node_to_dict(node):
    ND = {}
    if(len(node) == 0):
        return node.text
    for child in node:
        if child.tag not in ND:
            ND[child.tag] = node_to_dict(child)
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
    DT["locations"] = []
    DT["timings"] = []
    DT["calendar"] = node_to_dict(root.find(".//PlannedCalendar"))

    # Parsing
    for location in root.findall(".//Location"):
        DT["locations"].append(node_to_dict(location))
    for timing in root.findall(".//TimingAtLocation"):
        DT["timings"].append(node_to_dict(timing))
    return DT

# Tohle je zatm jen demo, ale parsuje to vsechny xmlka ve slozce
# urcene glob. promennou FOLDER_PATH
# pak to za kazdy soubor vytiskne info o vychozi a cilove stanici
# a calendar, kde je ulozene kdy jsou tyto casy platne
def main():
    filecount = 0
    print("*************************************************")
    for parsed in parsed_data_generator():
        filecount += 1
        print(f'Vychozi stanice: {parsed["locations"][0]}\n     {parsed["timings"][0]}\n')
        print(f'Cilova stanice:  {parsed["locations"][-1]}\n    {parsed["timings"][-1]}\n')
        print(f'Kalenar: {parsed["calendar"]}')
        print(f"************************************************* {filecount} ***************")
    print(f"Parsed {filecount} files.")

if __name__ == '__main__':
    main()