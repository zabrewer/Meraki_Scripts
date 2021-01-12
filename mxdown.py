import meraki
import csv

API_KEY = ''
orgid = ''
# next is optional, will filter for org names beginning with begin_filter
begin_filter = ''

api_call = meraki.DashboardAPI(
    api_key=API_KEY,
    # base_url="https://api.meraki.cn/api/v0/",
    base_url="https://api.meraki.com/api/v1/",
    # log_file_prefix=os.path.basename(__file__)[:-3],
    # log_path='',
    output_log=False,
    print_console=False,
    suppress_logging=True,
)


'''
mx_status

Takes 2 API calls - getOrganizationDevicesStatuses, getOrganizationDevices and combines relevant fields into one list
Arguments: orgid, devicefilter1, devicefilter2

Note: will make filters more robust w/ regex later
'''
def mx_status(orgid, devicefilter1, devicefilter2):
    mx_list = []
    status_list = []
    
    device_status = api_call.organizations.getOrganizationDevicesStatuses(organizationId=orgid, perPage=1000, total_pages='all')

    inventory = api_call.organizations.getOrganizationDevices(organizationId=orgid, perPage=1000, total_pages='all')

    # get all MX devices in inventory and append to mx_list
    def temp(inventory):
        for mx in inventory:
            if mx['model'].startswith(devicefilter1) or mx['model'].startswith(devicefilter2):
                # print(mx['model'])
                current_mx = {'name' : mx['name'], 'serial' : mx['serial'], 'mac' : mx['mac'], 'networkId' : mx['networkId'], 'model' : mx['model'], 'address' : mx['address'], 'lat' : mx['lat'], 'lng' : mx['lng'], 'url' : mx['url']} 
                mx_list.append(current_mx)

    
    # get devices from device status, compare SNs and append device status and other fields from getOrganizationDevicesStatuses API call to those in our list from getOrganizationDevices API call
    for device in device_status:
        for mx in mx_list:
            if device['serial'] == mx['serial']:
                mx_status = {'name' : mx['name'], 'serial' : mx['serial'], 'mac' : mx['mac'], 'status' : device['status'], 'lastReportedAt' : device['lastReportedAt'], 'OrgID' : orgid, 'networkId' : mx['networkId'], 'model' : mx['model'], 'address' : mx['address'], 'lat' : mx['lat'], 'lng' : mx['lng'], 'url' : mx['url']} 
                status_list.append(mx_status)
    
    return status_list


def get_orgs(org_filter):
    org_list = []

    all_orgs = api_call.organizations.getOrganizations()

    # get all orgs and append to org_list
    for org in all_orgs:
        if org['name'].startswith(org_filter):
            id_name = {'name' : org['name'], 'id' : org['id']} 
            org_list.append(id_name)
    
    return org_list

my_orgs = get_orgs(org_filter=begin_filter)

for org in my_orgs:
    print(org['id'] + ' | ' + org['name'])

def write_csv(orgname, status_list):
    with open(orgname + '_MX_Status.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = ['name', 'serial', 'mac', 'status', 'lastReportedAt', 'OrgID', 'networkId', 'model', 'address', 'lat', 'lng', 'url'])
            writer.writeheader()
            writer.writerows(device for device in status_list)

status_list = mx_status(orgid=orgid, devicefilter1='MX', devicefilter2='vMX')
write_csv(orgname=myorgs(org['name']), status_list=status_list)
