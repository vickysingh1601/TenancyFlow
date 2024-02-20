#
# Copyright 2023 Open Text.
# The only warranties for products and services of Open Text and its affiliates and licensors (“Open Text”)
# are as may be set forth in the express warranty statements accompanying such products and services.
# Nothing herein should be construed as constituting an additional warranty. Open Text shall not be liable
# for technical or editorial errors or omissions contained herein. The information contained herein is subject
# to change without notice..
#
# Except as specifically indicated otherwise, this document contains confidential information and a valid
# license is required for possession, use or copying. If this work is provided to the U.S. Government,
# consistent with FAR 12.211 and 12.212, Commercial Computer Software, Computer Software
# Documentation, and Technical Data for Commercial Items are licensed to the U.S. Government under
# vendor's standard commercial license.
#
# Author: Vikas Singh
#
#


# Libraries needed
import os
import sys
import re
import random
import string
from weakref import ref
import zipfile
import xml.etree.ElementTree as ET
import csv
import xml.dom.minidom as minidom
import pandas as pd
from datetime import datetime


# Generate random id for zone element
def generate_random_zone_id():
    random_id ="M"+generate_random_group_id()
    return random_id


# Generate random id for group element
def generate_random_group_id(length=24):
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+'
    random_string = ''.join(random.choice(characters) for _ in range(length - 3))
    return "0" + random_string + "=="


# Generate random id for package element
def generate_random_packg_id(length=22):
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+'
    random_string = ''.join(random.choice(characters) for _ in range(length - 3))
    return "_" + random_string + "=="


# Generate random version id
def generate_random_version_id(length=16):
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits + '-'
    random_string = ''.join(random.choice(characters) for _ in range(length - 5))
    return "AAAAA" + random_string


# Generate random string of certain length
def random_string(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


# Replace certain strings in the XML
def replace_string_in_xml(file_path,new_string):
    
    # Read the XML file
    with open(file_path, 'r') as file:
        xml_data = file.read()
    
     # Find and replace package name and id
    edited_xml_data = xml_data.replace("Tenant_Name_1.0", "Zone_Package_"+new_string)
    edited_xml_data = edited_xml_data.replace('_r5nh+YkBABCBSi4qFJiPUQ==', generate_random_packg_id())

    # Update the create time attribute
    now = datetime.now()
    create_time = now.strftime("%m-%d-%Y_%H:%M:%S.%f")[:-3]
    edited_xml_data = re.sub(r'createTime="([^"]*)"', f'createTime="{create_time}"', edited_xml_data)

    # Save the edited XML file
    edited_file_name = "Asset_Template.xml"
    edited_file_path = os.path.join(new_string, edited_file_name)

    with open(edited_file_path, 'w') as edited_file:
        edited_file.write(edited_xml_data)

    return edited_file_path


def create_zone_element(root, zone_name, endAdres, startAdres,dept_uri,dept_id):

    # Check if a Zone element with the given name already exists
    zone_exists = any(zone.attrib.get("name") == zone_name for zone in root.findall(".//Zone"))
   
    # If a Zone element doesn't exists then create a new zone element
    if not zone_exists:

        # Generate id and version id for zone
        zone_id = generate_random_zone_id()
        versionId = generate_random_version_id()

        # Print for logging the result
        print(f"Creating Zone '{zone_name}' with ID: {zone_id} and Version ID: {versionId}")  

        # Create a zone element with every sub-element required
        zone_elem = ET.Element('Zone', id=zone_id, name=zone_name, versionID=versionId, action="insert")

        childOf_elem = ET.SubElement(zone_elem, 'childOf')
        child_list_elem = ET.SubElement(childOf_elem, 'list')
        child_ref_elem = ET.SubElement(child_list_elem, 'ref', type="Group", uri=dept_uri, id=dept_id)

        dynamicAddressing_elem = ET.SubElement(zone_elem, "dynamicAddressing")
        dynamicAddressing_elem.text = "false"

        endAddress_elem = ET.SubElement(zone_elem, "endAddress")
        endAddress_elem.text = endAdres

        ntwrk_elem = ET.SubElement(zone_elem, "inNetwork")
        list1_elem = ET.SubElement(ntwrk_elem, "list")
        ref1_elem = ET.SubElement(
            list1_elem,
            "ref",
            {
                "type": "Network",
                "uri": "/All Networks/ArcSight System/Local",
                "id": "XdFUFQAEBABCAKaxkp9ga2g==",
                "externalID": "Local"
            }
        )
        startAddress_elem = ET.SubElement(zone_elem, "startAddress")
        startAddress_elem.text = startAdres

        return zone_elem
    else:
        print(f"Zone '{zone_name}' already exists")
        return None


def create_Zone(root, zonename, endAdres, startAdres,dept_uri,dept_id):

    # Call a function (create_zone_element) to create a new Zone element
    zone_elem = create_zone_element(root, zonename, endAdres, startAdres,dept_uri,dept_id)

    if zone_elem is not None:

        # Find the index of the Package element within the root XML structure
        package_index = None
        for index, elem in enumerate(root):
            if elem.tag == 'Package':
                package_index = index
                break

        if package_index is not None:

            # Insert the new Zone element above the Package element
            root.insert(package_index, zone_elem)


def create_group_element(group_name, group_id, version_id,uri_ref1,uri_ref1_id,link):

    #Create group element with every sub-element required
    group_elem = ET.Element('Group', id=group_id, name=group_name, versionID=version_id, action="insert")

    childOf_elem = ET.SubElement(group_elem, 'childOf')
    child_list_elem = ET.SubElement(childOf_elem, 'list')

    if link:
        child_ref_elem1 = ET.SubElement(child_list_elem, 'ref', type="Group", uri=uri_ref1, id=uri_ref1_id)
        child_ref_elem2 = ET.SubElement(child_list_elem, 'ref', type="Group", uri="/All Zones/ArcSight Solutions/Galaxy cyDNA/03.GLOBAL CORPS/", id="0YT4OcoEBABCAGOk9opLkMw==")
    else:
        child_ref_elem1 = ET.SubElement(child_list_elem, 'ref', type="Group", uri=uri_ref1, id=uri_ref1_id)

    containedResourceType_elem = ET.SubElement(group_elem, 'containedResourceType')
    containedResourceType_elem.text = "29"

    description_elem = ET.SubElement(group_elem, 'description')

    hasChild_elem = ET.SubElement(group_elem, 'hasChild')
    hasChild_list_elem = ET.SubElement(hasChild_elem, 'list')

    return group_elem


def create_or_update_group(root, group_name,group_id, target_uri,target_uri_id,link):
    uri_exists = False

    # Check if a group element with the given name and id already exists in the given parent group
    for group_element in root.findall(".//Group"):
        if group_element.get("name") == group_name and group_element.get("id") == group_id:
            for ref_element in group_element.findall(".//childOf/list/ref"):
                if ref_element.get("uri") == target_uri and ref_element.get("id") == target_uri_id:
                    uri_exists = True
                    break

    # If the group doesn't exist then generate a version id and create a group element along with logging the result
    if not uri_exists:
        version_id = generate_random_version_id()
        print(f"Creating Group '{group_name}' with ID: {group_id} and Version ID: {version_id}")        
        group_elem = create_group_element(group_name, group_id, version_id,target_uri,target_uri_id,link)
        return group_elem

    return None


def add_groups(root,group_name,group_id,target_uri,target_uri_id,link):

    # Call the function to create group element
    element = create_or_update_group(root, group_name,group_id,target_uri,target_uri_id,link)

    if element is not None:

        # Find the index of the Package element
        package_index = None
        for index, elem in enumerate(root):
            if elem.tag == 'Package':
                package_index = index
                break

        if package_index is not None:
            # Insert the new Group element above the Package element
            root.insert(package_index, element)

        return root
            
        
def add_has_child_ref_element_to_group(root,groupname,group_id, uri_info, uri_id):

    # Define the URI to validate and the specific group name
    target_uri = uri_info
    specific_group_name = groupname

    uri_exists = False  

    # Search for the URI within <hasChild>/list elements for the specific group name
    for group_element in root.findall(".//Group"):
        if group_element.get("name") == specific_group_name and group_element.get("id") == group_id:
            for ref_element in group_element.findall(".//hasChild/list/ref"):
                if ref_element.get("uri") == target_uri and ref_element.get("id") == uri_id:
                    uri_exists = True
                    break

    # If the URI does not exist for the specific group then it adds.
    if not uri_exists:
        for group_element in root.findall(".//Group"):
            if group_element.get("name") == specific_group_name and group_element.get("id") == group_id:
            # Create and append the <ref> child element
                hasChild_element = group_element.find(".//hasChild")
                list_element = hasChild_element.find(".//list")
                ref_element = ET.Element("ref")
                ref_element.set("type", "Group")
                ref_element.set("uri", target_uri)
                ref_element.set("id", uri_id)
                list_element.append(ref_element)


def add_has_child_ref_element_to_zone(root,groupname,group_id, uri_info, uri_id):

    # Define the URI to validate and the specific zone name
    target_uri = uri_info
    specific_group_name = groupname 

    uri_exists = False 

    # Search for the URI within <hasChild>/list elements for the specific zone name 
    for group_element in root.findall(".//Group"):
        for ref_element in group_element.findall(".//hasChild/list/ref"):
            if ref_element.get("id") == uri_id:
                # print("found")
                uri_exists = True
                break

    # If the URI does not exist for the specific zone then it adds
    if not uri_exists:
        for group_element in root.findall(".//Group"):
            if group_element.get("name") == specific_group_name and group_element.get("id") == group_id:

                # Create and append the <ref> child element
                hasChild_element = group_element.find(".//hasChild")
                list_element = hasChild_element.find(".//list")
                ref_element = ET.Element("ref")
                ref_element.set("type", "Zone")
                ref_element.set("uri", target_uri)
                ref_element.set("id", uri_id)
                list_element.append(ref_element)
  

def xml_update_with_Groups_Zones(csv_file_path, xml_file_path):

    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Read the CSV file into a DataFrame
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        # Defining dictionary for having unique entry of every URI
        countries = {}
        sectors = {}
        entities = {}
        departments = {}

        for row in csv_reader:

            # Access values based on column names
            country_name = row['Country']
            sec_name = row['Sector']
            entity_name = row['Entity']
            dept_name = row['Department']
            zone_name = row['zone_name']
            start_address = row['startAddress']
            end_address = row['endAddress']
            network_flag = row['NetworkFlag']

            # Create URI for each 
            country_uri= baseUri+country_name+"/"
            sector_uri= baseUri+country_name+"/"+sec_name+"/" 
            entity_uri =baseUri+country_name+"/"+ sec_name+"/"+entity_name+"/"
            dept_uri =baseUri+country_name+"/"+ sec_name+"/"+entity_name+"/"+dept_name+"/" 

            # Check if the dictionary contains the URI, if yes then take it else generate and make an entry in the dictionary.
            country_group_id = countries.get(country_uri, None)

            if country_group_id is None:
                country_group_id = generate_random_group_id()
                countries[country_uri]=country_group_id

            sec_group_id = sectors.get(sector_uri, None)

            if sec_group_id is None:
                sec_group_id = generate_random_group_id()
                sectors[sector_uri]=sec_group_id

            entity_group_id = entities.get(entity_uri, None)

            if entity_group_id is None:
                entity_group_id = generate_random_group_id()
                entities[entity_uri]=entity_group_id

            dept_group_id = departments.get(dept_uri, None)

            if dept_group_id is None:
                dept_group_id = generate_random_group_id()
                departments[dept_uri]=dept_group_id

            # Generate unique ID for country/sector/enetiy/department to create <group> element    
            # country_group_id = generate_random_group_id()
            # sec_group_id = generate_random_group_id()
            # entity_group_id = generate_random_group_id()
            # dept_group_id = generate_random_group_id()

            # Functions for generating group element needed for every row in the CSV
            add_groups(root,country_name,country_group_id,baseUri,base_group_id,True)
            add_groups(root,sec_name,sec_group_id,country_uri,country_group_id,False)
            add_groups(root,entity_name,entity_group_id,sector_uri,sec_group_id,False)    
            add_groups(root,dept_name,dept_group_id,entity_uri,entity_group_id,False)

            # Functions for adding <hasChild>/ref element to groups
            add_has_child_ref_element_to_group(root,base_group,base_group_id,country_uri, country_group_id)
            add_has_child_ref_element_to_group(root, country_name,country_group_id, sector_uri, sec_group_id)
            add_has_child_ref_element_to_group(root, sec_name,sec_group_id,entity_uri, entity_group_id)
            add_has_child_ref_element_to_group(root, entity_name,entity_group_id, dept_uri, dept_group_id)

            # Function for creating zone
            create_Zone(root, zone_name,end_address, start_address,dept_uri,dept_group_id)

            zone_id = extract_zone_id(root,zone_name)

            # Function for adding <hasChild>/ref element to zone
            add_has_child_ref_element_to_zone(root,dept_name,dept_group_id, dept_uri+zone_name, zone_id)

                        
    # Write the updated XML back to the file
    edited_file_name = "Updated_Asset_Template_zone.xml"
    tree.write(edited_file_name, xml_declaration=True, encoding='utf-8', method='xml')
    print(f"XML content has been written to {edited_file_name}")

    return edited_file_name
           

def extract_group_id(root,groupName):
    for groups in root.findall('Group'):
        if groups.attrib['name'] == groupName:
           group_id =groups.attrib['id']

           return group_id


def extract_zone_id(root,zoneName):
    for zones in root.findall('Zone'):
        if zones.attrib['name'] == zoneName:
           zone_id =zones.attrib['id']

           return zone_id


def insert_doctype(xml_content, doctype_name, dtd_location):
    doctype = f'<!DOCTYPE {doctype_name} SYSTEM "{dtd_location}">'
    
    return doctype


def insert_doctype_to_file(file_path):
    with open(file_path, "r") as file:
        xml_content = file.readlines()
   
# Specify the doctype name and DTD location
    doctype_name = "archive"
    dtd_location = "../../schema/xml/archive/arcsight-archive.dtd"

# Insert the DOCTYPE declaration
    xml_with_doctype = insert_doctype(xml_content, doctype_name, dtd_location)
    
# Write the modified XML back to the file
    xml_content.insert(2 - 1, xml_with_doctype)
    
    with open(file_path, 'w') as file:
        file.writelines(xml_content)
        return file_path


def create_zip_file(xml_file_path, edited_file_path, new_string):

    # Create a zip file
    zip_file_name = 'Asset_Template.zip'

    with zipfile.ZipFile(zip_file_name, 'w') as zip_file:

        # Add the edited XML file to the zip
        zip_file.write(edited_file_path, os.path.basename(edited_file_path))
       
        # Add the META-INF folder to the zip
        meta_inf_folder = os.path.join(os.path.dirname(xml_file_path), 'META-INF')

        for folder_name, _, file_names in os.walk(meta_inf_folder):
            for file_name in file_names:
                file_path = os.path.join(folder_name, file_name)
                zip_file.write(file_path, os.path.join('META-INF', file_name))

    # Change the file extension from .zip to .arb and rename the file
    arb_file_name = new_string +"_"+ "zones" + '.arb'
    arb_file_path = os.path.join(new_string, arb_file_name)
    os.rename(zip_file_name, arb_file_path)

    return arb_file_path


def get_non_empty_string_input(prompt):
    
    while True:
        user_input = input(prompt)

        # Check if the user input is empty or contains only spaces
        if not user_input.strip():
            print("Error: Input cannot be empty.")
        else:
            return user_input


def format_xml_file(input_file_path, output_file_path=None):
    # Read the XML file as a string
    with open(input_file_path, "r") as file:
        xml_str = file.read()

    # Parse and format the XML
    dom = minidom.parseString(xml_str)
    formatted_xml = dom.toprettyxml

    # Print or save the formatted XML
    if output_file_path:
        with open(output_file_path, "w") as output_file:
            output_file.write(formatted_xml)
        return output_file_path
    else:
        return formatted_xml


def format_unformatted_elements(input_file_path, output_file_path):

    # Parse the input XML file
    tree = ET.parse(input_file_path)
    root = tree.getroot()

    # Function to recursively format unformatted elements
    def format_element(element):
        if element.text is not None:
            element.text = '\n    ' + element.text.strip() + '\n    '
        else:
            element.text = '\n    '

        # Recursively format child elements
        for child in element:
            format_element(child)

    # Start formatting from the root element
    format_element(root)

    # Write the formatted XML to the output file
    tree.write(output_file_path, encoding='utf-8', xml_declaration=True)

    # Read the formatted XML from the output file
    with open(output_file_path, 'r') as output_file:
        formatted_xml = output_file.read()

    return formatted_xml


# Example usage
if len(sys.argv) != 3:
    print("Usage: python script_name.py <new_string> <csv_file_path>")
    sys.exit(1)

new_string = sys.argv[1]
csv_file_path = sys.argv[2]
xml_file_path = 'Default_asset_template.xml'
line_to_add = '<!DOCTYPE archive SYSTEM "../../schema/xml/archive/arcsight-archive.dtd">\n'
line_number = 2
baseUri= '/All Zones/ArcSight Solutions/Galaxy cyDNA/01.WATCH TENANTS/'
base_group ="01.WATCH TENANTS"
base_group_id ="0E+a9+H4BABCAFdsqNh15xQ=="


# Call all the function required for generating an arb
new_file_path = xml_update_with_Groups_Zones(csv_file_path, xml_file_path)
os.makedirs(new_string, exist_ok=True)
edited_file_path = replace_string_in_xml(new_file_path,new_string) 
edited_file_path = insert_doctype_to_file(edited_file_path)
arb_file_path = create_zip_file(new_file_path, edited_file_path, new_string)


# Logging the result
print(f"XML and ARB files created in the directory: {new_string}")
print(f"XML file path: {edited_file_path}")
print(f"ARB file path: {arb_file_path}")