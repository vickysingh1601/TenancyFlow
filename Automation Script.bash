#!/bin/bash
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

# Print welcome message
echo
echo "===================================================================="
echo "           Customer Onboarding/Offboarding Automation"
echo "===================================================================="
echo

pwd="$(pwd)"

# # Function to prompt for a user confirmation
# prompt_confirm() {
#   while true; do
#     read -r -p "${1:-Continue?} [y/n]: " REPLY
#     case $REPLY in
#       [yY]) echo ; return 0 ;;
#       [nN]) echo ; return 1 ;;
#       *) echo; echo "Invalid response!" ;;
#     esac
#   done
# }

is_number() {
    [[ "$1" =~ ^[0-9]+$ ]]
}

try_again() {
    while true; do
            read -r -p "Do you want to try again? [y/n]: " retry_response
            echo
            case $retry_response in
                [nN]) 
                    echo -e "Exiting the script.\n"
                    exit 1
                    ;;
                [yY])
                    echo -e "Continuing...\n"
                    break
                    ;;
                *)
                    echo -e "Invalid Input\n"  
            esac
        done
}

process_zonemodel() {
    # Actual path of the zonemodel CSV file
    csv_file="$pwd/zonemodel.csv"

    # Check if the file exists
    if [ ! -f "$csv_file" ]; then
        echo -e "Error: File not found.\n"
        exit 1
    fi

    # Use awk to extract unique entries under the 'Entity' column
    unique_entities=$(tail -n +2 "$csv_file" | cut -d ',' -f 3 | sort | uniq)

    # Print unique entities
    for entity_name in $unique_entities; do
        while true; do
            read -r -p "Provide Customer ID for $entity_name: " temp_customer_id
            if is_number "$temp_customer_id"; then
                break
            else
                echo -e "Invalid input. Please enter a numeric value.\n"
            fi
        done
        echo -e "\nAssociated tenants for $entity_name:\n"

        # Display unique names of 'zone_name' for each unique entity
        names=$(awk -F ',' -v entity="$entity_name" '$3 == entity {gsub(/:[^:]*$/, "", $5); print $5}' "$csv_file" | sort -u)

        # Use a for loop to iterate over the associated zone names
        for zone_name in $names; do
            while true; do
                read -r -p "Provide Tenant ID for $zone_name: " temp_tenant_id
                if is_number "$temp_tenant_id"; then
                    break
                else
                    echo -e "Invalid input. Please enter a numeric value.\n"
                fi
            done
            echo
            
            # Create JSON and associated directory for the tenant
            python json_creator.py "$entity_name" "$temp_customer_id" "$zone_name" "$temp_tenant_id" "$csv_file"

            # Move to tenant-onboarding-template-creator for script execution
            cd tenant-onboarding-template-creator || echo "ERROR: tenant-onboarding-template-creator didn't found"

            # Run script for creating tenant package
            python ArcSight_Template_Creator.py "$entity_name" "$temp_tenant_id"

            # Move back to original working directory
            cd ..

            # Creating job for the tenant
            echo -e "Creating job for $entity_name:$zone_name\n"

        done
    done
    echo
    if [ "$(echo "$unique_entities" | wc -l)" -eq 1 ]; then
        single_entry="$unique_entities"
        echo -e "Generating zone model arb for $single_entry...\n"
        python Asset_Template_Creator.py "$single_entry" "$csv_file"
        rm "$pwd/Updated_Asset_Template_zone.xml"
        mv "$csv_file" "$pwd/$single_entry"
    else
        echo -e "Skipping zone model arb creation as multiple customer are present in the questionaire.\n"
        mv "$csv_file" "$pwd/dump"
        echo -e "Use $pwd/dump/zonemodel.csv for manually creating zonemodel inside ESM.\n"
    fi

    echo -e "\n***Import zone as well as all tenant packages into the ESM for complete onboarding.***\n"
}

# Onboarding wizard
Onboarding() {

    onboarding_questionaire_path=""

    echo
    echo "===================================================================="
    echo "                      Onboarding wizard"
    echo "===================================================================="
    while true; do
        echo
        echo "Provide the Onboarding Questionnaire file location:"
        read -r onboarding_questionnaire_path
        echo

        if [ -f "$onboarding_questionnaire_path" ]; then
            echo -e "File exists. Proceeding...\n"
            echo -e "Fetching the required data from the sheet\n"
            python Data_manipulator.py "$onboarding_questionnaire_path"
            process_zonemodel
            break
        else
            echo -e "Error: The specified file does not exist. Please provide a valid file location.\n"
            try_again
        fi
    done
}

#
Offboarding_tenant() {

    customer_name=""
    customer_id=""
    tenant_name=""
    tenant_id=""

    echo
    echo "===================================================================="
    echo "                      Offboarding Tenant"
    echo "===================================================================="
    echo

    while true; do
        echo "Provide the name of the Customer:"
        read -r customer_name

        echo "Provide the id of the Customer:"
        read -r customer_id

        echo "Provide the name of the Tenant:"
        read -r tenant_name

        echo "Provide the id of the Tenant:"
        read -r tenant_id

        customer_directory="$pwd/../config/$customer_name"
        tenant_directory="$customer_directory/$tenant_name"
        echo
        echo -e "Checking if the directory and JSON file exist...\n"
        if [ -d "$tenant_directory" ]; then

            echo -e "Directory exists.\n" 
            echo -e "Checking for JSON files...\n"
            json_files=$(find "$tenant_directory" -maxdepth 1 -type f -name "*.json")

            if [ -n "$json_files" ]; then

                echo -e "JSON exists.\n"
                read -r -p "Confirm if you want to offboard the Tenant? [y/n]: " confirm

                echo
                case $confirm in
                    [yY]) 
                        echo -e "Validating JSON with the given values...\n"
                        # Run json_validator.py with provided input and capture its output
                        validator_output=$(python json_validator.py "$customer_name" "$customer_id" "$tenant_name" "$tenant_id")
                        # Check if the output contains the string "Found"
                        if [ "$validator_output" == "Found" ]; then
                            echo -e "Value is Found. Proceeding...\n"
                            
                            # Disabling entry from the hawkeye.db
                            echo -e "Disabling jobs for $tenant_name\n"
                            #cy disable_tenant "$tenant_id"
                            
                            # Deleting the tenant associated JSON and directory
                            echo -e "JSON files found. Deleting...\n"
                            rm "$tenant_directory"/*.json
                            echo -e "JSON files deleted.\n"
                            echo -e "Deleting the associated tenant directory.\n"
                            rm -r "$tenant_directory"

                            # Guide for .arb file removal
                            echo -e "****Remove ${customer_name}_${tenant_id}.arb from the ESM for complete offboarding.****\n"

                            break
                        else
                            echo -e "json_validator.py output: $validator_output\n"
                        fi
                        ;;
                    [nN])
                        echo -e "Skipping the offbaording...\n"
                        break
                        ;;
                    *)
                        echo -e "Invalid Input\n"
                        ;;
                esac
               # break  # Exit the loop if JSON files are found and deleted
            else
                echo -e "No JSON files found in the directory.\n"
            fi
        else
            echo -e "Error: Directory does not exist. Please provide a valid directory path.\n"
        fi
        try_again
    done

    # echo "Provide the name of the Customer:"

    # echo "Provide the name of the Tenant:"

    # echo "Checking if the directory and JSON file exists"
    # if [ -d "$directory_path" ]; then
    #     echo "Directory exists. Checking for JSON files..."

    #     json_files=$(find "$directory_path" -maxdepth 1 -type f -name "*.json")

    #     if [ -n "$json_files" ]; then
    #         echo "JSON files found. Deleting..."
    #         rm "$directory_path"/*.json
    #         echo "JSON files deleted."
    #     else
    #         echo "No JSON files found in the directory."
    #     fi
    # else
    #     echo "Error: Directory does not exist."
    # fi
}

#
Offboarding_customer() {

    customer_name=""
    customer_id=""

    echo
    echo "===================================================================="
    echo "                      Offboarding Customer"
    echo "===================================================================="
    echo

    while true; do
        echo "Provide the name of the Customer:"
        read -r customer_name

        echo "Provide the id of the Customer:"
        read -r customer_id
        
        echo        

        customer_directory="$pwd/../config/$customer_name"

        echo -e "Checking if the directory exist...\n"
        if [ -d "$customer_directory" ]; then
            echo -e "Directory exists.\n"

            read -r -p "Confirm if you want to offboard the Customer? [y/n]: " confirm
            echo

            case $confirm in
                [yY])
                    output_file="$pwd/tenant_entries.txt"
                    echo -e "Provide information of every tenant associated with the $customer_name\n"
                    while true; do
                        tenant_name=""
                        tenant_id=""

                        # Prompt the user for input
                        echo "Enter tenant_name (or 'exit' to quit):"
                        read -r tenant_name

                        # Check if the user wants to exit
                        if [ "$tenant_name" == "exit" ]; then
                            echo
                            echo -e "Exiting the loop.\n"
                            break
                        fi

                        echo "Enter tenant_id: "
                        read -r tenant_id
                        echo

                        # Check if the entry already exists in the output file
                        if grep -q "tenant_name: $tenant_name, tenant_id: $tenant_id" "$output_file"; then
                            echo -e "Entry already exists. Not adding to $output_file.\n"
                        else
                            # Run json_validator.py with provided input and capture its output
                            validator_output=$(python json_validator.py "$customer_name" "$customer_id" "$tenant_name" "$tenant_id")

                            # Check if the output contains the string "Found"
                            if [ "$validator_output" == "Found" ]; then
                                echo -e "Value is Found. Adding entry to $output_file...\n"
                                echo "tenant_name: $tenant_name, tenant_id: $tenant_id" >> "$output_file"
                            else
                                echo -e "json_validator.py output: $validator_output\n"
                                echo -e "Entry not added.\n"
                            fi
                        fi
                    done
                    # Check if entries in tenant_entries.txt match with the directories in customer_directory
                    num_tenants=$(grep -c "tenant_name" "$output_file")
                    actual_num_tenants=$(find "$customer_directory" -mindepth 1 -maxdepth 1 -type d | wc -l)

                    if [ "$num_tenants" -eq "$actual_num_tenants" ]; then
                        echo -e "Entries match the number of tenants. Processing entries in $output_file...\n"

                        # Process each tenant entry in tenant_entries.txt
                        while IFS=, read -r tenant_name_entry tenant_id_entry; do
                            # Extracting tenant_id using awk
                            current_tenant_id=$(echo "$tenant_id_entry" | awk '{print $2}')
                            echo -e "Running cy disable_tenant $current_tenant_id\n"
                            # cy disable_tenant "$current_tenant_id"
                        done < "$output_file"

                        #Remove the output file after processing
                        rm "$output_file"

                        #remomving customer directory
                        echo -e "Removing customer directory...\n"
                        rm -rf "$customer_directory"
                                                
                        # Guide for removing .arb file
                        echo -e "****Remove all ${customer_name}_<tenant_id>.arb from the ESM for complete offboarding.****\n"
                        
                        break
                    else
                        echo -e "Values provided do not match the number of tenants in $customer_directory.\n"
                    fi
                    ;;
                [nN])
                    echo -e "Skipping the offbaording...\n"
                    break
                    ;;
                *)
                    echo -e "Invalid Input\n"
                    ;;
            esac
        else
            echo -e "Error: Directory does not exist. Please provide a valid directory path.\n"
        fi
        try_again
    done
}

# Offboarding wizard
Offboarding() {
    echo
    echo "===================================================================="
    echo "                      Offboarding wizard"
    echo "===================================================================="
    echo
    while true; do
        echo "Choose one of the options to proceed:"
        echo "0. Offboarding the existing Tenant"
        echo -e "1. Offboarding the existing customer\n"
        read -r -p "Choose[0/1]: " reply
        echo
        case $reply in
            0)
                Offboarding_tenant
                break
                ;;
            1)
                Offboarding_customer
                break
                ;;
            *)
                echo -e "Invalid option! Please enter 0 or 1.\n"
                try_again
                ;;
        esac
    done
}

# walk_through function for guiding the customer through the entire automation process
walk_through() {
    while true; do
        # prompt for choosing the 
        echo "Choose one of the options to proceed:"
        echo "0. Onboarding new tenant/customer"
        echo -e "1. Offboarding the existing tenant/customer\n"
        read -r -p "Choose[0/1]: " reply
        echo
        case $reply in
            0)
                Onboarding
                break
                ;;
            1)
                Offboarding
                break
                ;;
            *)
                echo -e "Invalid option! Please enter 0 or 1.\n"
                try_again
                ;;
        esac
    done
}

main() {
    walk_through
    echo "$onboarding_questionaire_path"
}

### Main: starts here ###
main "$@"