import json
import sys
import os

def check_tenant_info(customer_name, customer_id, tenant_name, tenant_id):

    # Construct the expected directory path
    directory_path = os.path.join(os.path.dirname(os.getcwd()), "config", customer_name, tenant_name) 

    # Construct the expected dictionary from the command line arguments
    expected_info = {
        "customer_name": customer_name,
        "customer_id": customer_id,
        "tenant_name": tenant_name,
        "tenant_id": tenant_id
    }

    # Check if the specified directory exists
    if not os.path.isdir(directory_path):
        print(f"Error: Directory {directory_path} not found.")
        return

    # Get a list of all files in the specified directory
    files_in_directory = os.listdir(directory_path)

    # Filter out only the JSON files
    json_files = [file for file in files_in_directory if file.endswith(".json")]

    # If none JSON files found
    if not json_files:
        print(f"Error: No JSON files found in {directory_path}.")
        return

    # Iterate through each JSON file and check if values match
    for json_file in json_files:
        file_path = os.path.join(directory_path, json_file)
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                print(f"Error: Unable to parse JSON from {file_path}. Skipping.")
                continue

        # Check if the values match
        if data.get("customer_name") == expected_info["customer_name"] and \
           data.get("customer_id") == expected_info["customer_id"] and \
           data.get("tenant_name") == expected_info["tenant_name"] and \
           data.get("tenant_id") == expected_info["tenant_id"]:
            print("Found")
            return

    # If loop completes without finding a match
    print("Not Found: Values do not match in any JSON file in", directory_path)

if __name__ == "__main__":
    
    # Check if the correct number of command line arguments is provided
    if len(sys.argv) != 5:
        print("Usage: python script.py customer_name customer_id tenant_name tenant_id")
    else:

        # Extract command line arguments
        customer_name, customer_id, tenant_name, tenant_id = sys.argv[1:]

        # Call the function to check tenant info
        check_tenant_info(customer_name, customer_id, tenant_name, tenant_id)
