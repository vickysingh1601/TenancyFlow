Arcsight_Template_Creator.py
----------------------------

This python script takes XML file as an input which will be constant in our case and will be a part of this script folder.

After reading out the file following changes will be made:
1. Changing tenantid at every place.
2. Changing versionID for resources like Group, Rule, Report, ActiveList etc.
3. Changing id of resources along with the places where references of these resources are given.
4. Changing id of SchedulesTask associated with the report.

Note: New versionID will have few starting character different from the old one which will be generated randomly while the new id for resources will have tenantid embedded in the old id which will result in having unique id per resource per tenant as tenantid will be unique to the tenant. After all the changes the file will be zipped with META-INF and will be converted into arb file.

How to run the script:
1. Prepare an environment and IDE for python 3.11.
2. Open the "Generate Package For Tenant Report" folder in the IDE.
3. Run the "Arcsight_Template_Creator.py" script.
4. Enter the tenantID for the respective tenant.

The result of the script which is arb file along with the final XML file will be generated in the same location of the script inside the folder(name of folder = <TenantID>)

Note: Avoid opening and editing the default files available in the "Generate Package For Tenant Report" folder.