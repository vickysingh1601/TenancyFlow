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

import os
import re
import sys
import shutil
import random
import string
import zipfile

# Generate a random string with the starting 5 characters replaced.
def generate_random_string(length, old_string):
    random_chars = ''.join(random.choice(string.ascii_letters) for _ in range(5))
    new_string = random_chars + old_string[5:]
    return new_string[:length]

def random_string(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    
def random_character(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

# Generate new resouce id with tenantID embedded after 3rd place
def generate_new_id(old_id, tenantID):
    return old_id[:3] + tenantID + random_character(3) + old_id[3 + len(tenantID) + 3:]

def generate_new_id_group(old_id, customerName):
    return old_id[:3] + customerName + old_id[3 + len(customerName):]

def replace_string_in_xml(file_path, old_string, new_string):
    # Read the XML file
    with open(file_path, 'r') as file:
        xml_data = file.read()
    # # Perform the replace operation
    # edited_xml_data = xml_data.replace(old_string, new_string)
    # Find and replace versionID in Group, Rule, Report, ActiveList, and Query
    tags = ['Rule', 'Report', 'ActiveList', 'Query', 'ScheduledTask']
    for tag in tags:
        pattern = r'<{}[^>]+versionID="([^"]+)"[^>]*>'.format(tag)
        xml_data = re.sub(pattern, lambda m: m.group(0).replace(m.group(1), generate_random_string(len(m.group(1)),m.group(1))), xml_data)

    # Perform the TenantID replace operation
    edited_xml_data = xml_data.replace(old_string, new_string)

    # Changing VersionID of required groups
    Groups_VersionId=['AAAAIes37KN4FgV+','AAAACVfW5oog+yOi','AAAABLC0xRHnza+d']
    for id in Groups_VersionId:
        edited_xml_data = edited_xml_data.replace(id, generate_random_string(len(id),id))

    # Find and replace tableID
    edited_xml_data = edited_xml_data.replace('7QLXXJ', random_string(6))
    
    # Find and replace CustomerName
    edited_xml_data = edited_xml_data.replace('CustomerName', customer)

    # Find and replace Package related changes
    edited_xml_data = edited_xml_data.replace('Tenant_Template', 'Tenant_'+customer+'_'+new_string)
    edited_xml_data = edited_xml_data.replace('_CgFXPokBABCBClCtScuTLg==', generate_new_id('_CgFXPokBABCBClCtScuTLg==',new_string))

    # Perform the ActiveList related changes
    #edited_xml_data = edited_xml_data.replace('HFOQO6YIBABCAO6HwzWzR3Q==', generate_new_id('HFOQO6YIBABCAO6HwzWzR3Q==',new_string))
    edited_xml_data = edited_xml_data.replace('Hlzk2U4kBABDTXTzkUZ0tTg==', generate_new_id('Hlzk2U4kBABDTXTzkUZ0tTg==',new_string))

    # Perform the Group ID related changes
    Groups_Resource_id=['0vkTJL4YBABCA1AvDUpxojw==','0RXrPr4gBABD0KV8Jx2Pz7g==','0FfuE4YgBABCYUccdQK8nYQ==']
    for id in Groups_Resource_id:
        edited_xml_data = edited_xml_data.replace(id,generate_new_id(id,new_string))
 
    # Perform the Query ID related changes
    #edited_xml_data = edited_xml_data.replace('[vrBG6YIBABDf7ipz6j2+MQ==', generate_new_id('[vrBG6YIBABDf7ipz6j2+MQ==',new_string))
    edited_xml_data = edited_xml_data.replace('[c1f8UokBABCJRBYdZdgryA==', generate_new_id('[c1f8UokBABCJRBYdZdgryA==',new_string))

    # Perform the Report ID related changes
    edited_xml_data = edited_xml_data.replace('9FPlE6YIBABCo1offqidZvA==', generate_new_id('9FPlE6YIBABCo1offqidZvA==',new_string))

    # Perform the Rule ID related changes
    edited_xml_data = edited_xml_data.replace('55nvPr4gBABD0MEO9bHR-Cg==', generate_new_id('55nvPr4gBABD0MEO9bHR-Cg==',new_string))
    
    # Perform the Report Group ID changes
    edited_xml_data = edited_xml_data.replace('0Gc83k4kBABCUHKbGZPkw8A==', generate_new_id_group('0Gc83k4kBABCUHKbGZPkw8A==',customer))
    
    # Perform the Archive Report Group ID changes
    edited_xml_data = edited_xml_data.replace('0aIU9k4kBABCUHVb8cEqndw==', generate_new_id_group('0aIU9k4kBABCUHVb8cEqndw==',customer))

    # Perform the ScheduledTask related changes for Report
    edited_xml_data = edited_xml_data.replace(';mAzML4YBABCA32gS6g0fyQ==', generate_new_id(';mAzML4YBABCA32gS6g0fyQ==',new_string))

    # Save the edited XML file
    edited_file_name = "Tenant_Template.xml"
    edited_file_path = os.path.join(os.getcwd(),new_string, edited_file_name)

    with open(edited_file_path, 'w') as edited_file:
        edited_file.write(edited_xml_data)

    return edited_file_path

def create_zip_file(xml_file_path, edited_file_path, new_string):
    # Create a zip file
    zip_file_name = 'Tenant_Template.zip'
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
    arb_file_name = customer + '_' + new_string + '.arb'
    arb_file_path = os.path.join(os.getcwd(),new_string, arb_file_name)
    os.rename(zip_file_name, arb_file_path)
    try:
        source_directory = os.path.join(os.getcwd(),new_string)
        destination_directory = os.path.join(os.path.dirname(os.getcwd()),customer,new_string)
        shutil.move(source_directory, destination_directory)
        print(f"Tenant package for {new_string} has been created under {destination_directory}")
    except Exception as e:
        print(f"Error moving directory: Tenant package for {new_string} has been created under {source_directory}")

    return arb_file_path

def get_non_empty_string_input(prompt):
    while True:
        user_input = input(prompt)

        # Check if the user input is empty or contains only spaces
        if not user_input.strip():
            print("Error: Input cannot be empty.")
        else:
            return user_input

# Example usage
xml_file_path = 'Default_format.xml'
old_string = '10010'

if len(sys.argv) != 3:
    print("Usage: python script_name.py <customer_name> <tenant_id>")
    sys.exit(1)

customer = sys.argv[1]
new_string = sys.argv[2]

# Create a directory with the new_string name
os.makedirs(new_string, exist_ok=True)
edited_file_path = replace_string_in_xml(xml_file_path, old_string, new_string)
arb_file_path = create_zip_file(xml_file_path, edited_file_path, new_string)

# print(f"XML and ARB files created in the directory: {new_string}")
# print(f"XML file path: {edited_file_path}")
# print(f"ARB file path: {arb_file_path}")
