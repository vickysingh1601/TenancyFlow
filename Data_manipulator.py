import pandas as pd
import ipaddress
import os
import sys

def calculate_start_end_addresses(cidr):
    if pd.isna(cidr):
        return None, None  # Return None if CIDR is NaN
    try:
        network = ipaddress.IPv4Network(cidr, strict=False)
        return str(network.network_address), str(network.broadcast_address)
    except ipaddress.AddressValueError as e:
        print(f"Error processing CIDR {cidr}: {e}")
        return None, None

# Check if the correct number of command-line arguments is provided
if len(sys.argv) != 2:
    print("Usage: python script_name.py path_to_ArcSight_cyDNA_Onboarding_Questionnaire.xlsx")
    sys.exit(1)

# Get the Excel file path from the command-line argument
file_path = sys.argv[1]

# Verify that the file path exists
if not os.path.exists(file_path):
    print(f"Error: File '{file_path}' not found.")
    sys.exit(1)

# Get the current working directory
current_directory = os.getcwd()

# Read the Excel file, skip the first 11 rows to start from B12
df_asns = pd.read_excel(file_path, sheet_name='ASNs', skiprows=11)

# Skip rows where '#' column contains 'EXMPL'
df_asns = df_asns[df_asns['#'] != 'EXMPL']

# Read the 'Entity' value from a different sheet starting from cell I9
entity_sheet = pd.read_excel(file_path, sheet_name='General Info', header=None, skiprows=8, usecols=[8], names=['Entity'])
entity_value = entity_sheet.iloc[0, 0]

# Exclude rows where any field is empty
df_asns = df_asns.dropna(subset=['Country', 'Entity Sector', 'ASN Name', 'Entity Name', 'ASN CIDR'])

# Combine 'Entity Name' and 'ASN CIDR' for 'Zone name' for each row
df_asns['Zone name'] = df_asns.apply(lambda row: str(row['Entity Name']).replace('nan', '') + ':' + str(row['ASN CIDR']).replace('nan', ''), axis=1)

# Process each row and create a new row in the output DataFrame
output_rows = []
processed_cidrs = set()  # To keep track of unique CIDRs

for index, row in df_asns.iterrows():
    asn_cidr = row['ASN CIDR']

    # Check if the CIDR is already processed
    if asn_cidr in processed_cidrs:
        print(f"ASN CIDR {asn_cidr} already present. Skipping the row.")
        continue

    country = row['Country']
    sector = row['Entity Sector']
    department = row['ASN Name']
    zone_name = row['Zone name']
    start_address, end_address = calculate_start_end_addresses(asn_cidr)

    output_rows.append({
        'Country': country,
        'Sector': sector,
        'Entity': entity_value,
        'Department': department,
        'zone_name': zone_name,
        'startAddress': start_address,
        'endAddress': end_address,
        'NetworkFlag': 'False'
    })

    processed_cidrs.add(asn_cidr)  # Add the CIDR to the set

# Create a new data frame with the extracted values
df_new = pd.DataFrame(output_rows)

# Construct the path to the new CSV file in the current working directory
new_csv_file_path = os.path.join(current_directory, 'zonemodel.csv')

# Save the new data frame to a new CSV file
df_new.to_csv(new_csv_file_path, index=False)
