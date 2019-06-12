
#######################################################################################################################
#
# claim_licenses.py
#
# Overview
# Quick script I wrote to help a customer claim multiple meraki licenses from an excel file.
# The script expects CSV file called "licenses.csv" in the same directory as the script
# The CSV file must have 3 column headers in the first row - lic_key, lic_mode, and org_id
#
# lic_key column should contain Meraki Dashboard licenses (license keys only, if you want SNs or order #s, modify the script) 
# lic_mode column can ONLY be renew or addDevices as per the Meraki Dashboard API for claiming licenses
# org_id column should be the ORGID where you want the licenses claimed (needed to support multiple orgs for my use case)
#
# one other note - be aware API rate limit of 5 calls per sec per org especially if you have a lot of lic keys
# you can utilize exponential backoff or do something as simple as to add a time.sleep(X) to the for loop on line 58
#
# Provided with NO WARRANTY of any kind
#
# Dependencies
# - Python 3.6
# - requests module
# - meraki module
#
#######################################################################################################################

from meraki import meraki
import csv

# feel free to remove all of this to speed up the script
print("This script loops through a csv file and adds the licenses in the file to a Meraki org")  
print("The file must be named licenses.csv and its column headers must be named lic_key, lic_mode, and org_id in that order")
print("The lic_key column must contain valid Meraki device licenses")  
print("The lic_mode column must contain either renew or addDevices as per the Meraki API documentation")
print("The org_id column must contain the Meraki Dashboard orgID where you want the licenses claimed")
print("\n")

# if you remove the next line, hard code the apikey i.e. apikey = "123456789"
apikey = input("Copy and paste your API Key here:  ")

# if you remove the next line, delete 'if script_mode = '1' line, delete, the elif script_mode line, and the final 2 lines of the script
# after removing those lines, remove 4 lead spaces from every line below this one
# after this, you can also delete the first "with open" code block
script_mode = input("To run the script in TEST MODE, type 1\n\nTo run the script against the API, type 2\n\nYour choice (1 or 2)?:  ")

if script_mode == '1':
    with open("licenses.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        lic_count = 0
        for dct in reader:
            lic_count += 1
            print(f"{dct['lic_key']} {dct['lic_mode']} {dct['org_id']}")        
        print(f'Would have processed {lic_count} licenses.')
elif script_mode == '2':
    with open("licenses.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        lic_count = 0
        for dct in reader:
            lic_count += 1
            lic_key = dct['lic_key']
            lic_mode = dct['lic_mode']
            org_id = dct['org_id']
            print('Attempting to add license ' + lic_key + '...')
            MyLicClaim = meraki.claim(apikey, orgid=org_id, serial=None, licensekey=lic_key, licensemode=lic_mode, orderid=None, suppressprint=True)
            if MyLicClaim is not None:
                print('Meraki Dashboard API returned the following result for ' + lic_key + ' :  ' + MyLicClaim[0])
                print('\n')
            else:
                print(MyLicClaim)
            #print(apikey, orgid, serial, licensekey, licensemode, orderid)
        print(f'Processed {lic_count} licenses.  See returned HTTP status codes above for individual status.')
        print('hint:  404 codes are often caused by mistyped API key, mistyped Org ID, or an api key that does not have access to the Org')
else:
    print('only 1 or 2 are valid answers for script mode')