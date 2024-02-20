import os
import json
import sys
import csv

def create_directory_structure(customer_name, tenant_name):

    # Paths for customer and tenant directories
    customer_directory = os.path.join(os.path.dirname(os.getcwd()), "config", customer_name)
    tenant_directory = os.path.join(customer_directory, tenant_name)

    # Create directories if they don't exist
    if not os.path.exists(tenant_directory):
        os.makedirs(tenant_directory)
    else:
        print(f"Directory '{tenant_directory}' already exists.")

    return tenant_directory

def create_json_file(directory, customer_name, tenant_name, customer_id, tenant_id, path_of_zonemodel):

    # Get information from the provided ZoneModel file
    slots = get_slots_from_zonemodel(path_of_zonemodel, customer_name, tenant_name)

    # Create a dictionary representing the JSON data
    data = {
        "customer_name": customer_name,
        "tenant_name": tenant_name,
        "tenant_id": tenant_id,
        "customer_id": customer_id,
        "description": f"Data Harvester job for {tenant_name}:{tenant_id}",
        "start_date": "today - 30",
        "end_date": "today",
        "dta_job": "false",
        "custom_log_group": "",
        "slots": slots,
        "queries": [
            {
                "query_type": "flows",
                "exclude_proto": "1",
                "num_octets": "7000000-999999999999999"
            },
            {
                "query_type": "useragents"
            },
            {
                "query_type": "dionaea_honeypot"
            },
            {
                "query_type": "ddos_attacks"
            },
            {
                "query_type": "beacons"
            },
            {
                "query_type": "compromised_hosts"
            }
        ]
    }

    # Create JSON with all the required information
    json_file_path = os.path.join(directory, "tenant.json")

    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=2)

    print(f"JSON file created at: {json_file_path}")

def check_zonemodel_file(path_of_zonemodel):
    if not os.path.exists(path_of_zonemodel):
        print(f"Error: Zonemodel file not found at {path_of_zonemodel}. Please provide a valid path.")
        sys.exit(1)

def get_slots_from_zonemodel(path_of_zonemodel, customer_name, tenant_name):
    slots = []
    with open(path_of_zonemodel, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            entity = row.get('Entity', '')
            zone_name = row.get('zone_name', '')
            if entity == customer_name and zone_name.startswith(tenant_name + ":"):
                # Extract the value after ':'
                value_after_colon = zone_name.split(':', 1)[1].strip()
                slots.append(value_after_colon)

    return ','.join(slots)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python script_name.py $customer_name $customer_id $tenant_name $tenant_id $path_of_zonemodel")
        sys.exit(1)

    customer_name, customer_id, tenant_name, tenant_id, path_of_zonemodel = sys.argv[1:]

    check_zonemodel_file(path_of_zonemodel)

    tenant_directory = create_directory_structure(customer_name, tenant_name)
    create_json_file(tenant_directory, customer_name, tenant_name, customer_id, tenant_id, path_of_zonemodel)

    # print(f"Directory structure and JSON file created for {customer_name}/{tenant_name}")
