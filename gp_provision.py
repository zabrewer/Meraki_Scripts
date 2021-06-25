import meraki
import csv_tools

__author__ = 'Zach Brewer'
__email__ = 'zbrewer@cisco.com'
__version__ = '0.0.8'
__license__ = 'MIT'

# network tag to find for target networks (Group policy will be created in networks tagged with this tag)
gp_networktag = 'tag1'
apikey = '1234'
# empty policy name to use - cannot currently be used in a network group policy (script checks for existence)
empty_policyname = 'MacAUTH'
csv_file = 'clients.csv'

print(f'gp_provision.py\nThis script performs the following actions:\n')
print(f'1) Gets all orgs available to the API key provided.')
print(f'2) Gets all networks within those orgs.')
print(f'3) Looks for networks tagged with the tag name defined in the gp_tag variable.')
print(f'4) Creates an empty group policy (if the name is not already taken) for each network in Step #3.')
print(f'5) Reads mac addresses from csv file.')
print(f'6) Provisions clients from mac addresses and associates group policy from step #4.\n\n')

input('Press Enter to continue...')

class call_dashboard(object):
    def __init__(self, apikey):
        """call to dashboard API and makes session available to other methods in this class

        """
        self.api_session = meraki.DashboardAPI(
        api_key=apikey,
        base_url="https://api.meraki.com/api/v1/",
        output_log=False,
        print_console=False,
        suppress_logging=True,
        )

    def get_orgs(self):
        return self.api_session.organizations.getOrganizations()
    
    def get_networks(self, orgid):
        return self.api_session.organizations.getOrganizationNetworks(organizationId=orgid)
    
    def get_policy(self, networkid, policyid):
        return self.api_session.networks.getNetworkGroupPolicy(networkId=networkid, groupPolicyId=policyid)
    
    def get_policies(self, networkid):
        return self.api_session.networks.getNetworkGroupPolicies(networkId=networkid)
    
    def create_policy(self, networkid, policy_name):
        return self.api_session.networks.createNetworkGroupPolicy(networkId=networkid, name=policy_name)
    
    def provision_client(self, networkid, clients, policy_id):
        return self.api_session.networks.provisionNetworkClients(networkId=networkid, clients=clients, devicePolicy='Group policy', groupPolicyId=policy_id)

api_session = call_dashboard(apikey=apikey)

def create_dict(data: dict, fields_order: list, append_data=None):
    """takes a nested dict passed to it and orders the k,v

    create_dict takes all nested dicts in an array (e.g. JSON)
    1) only keeps k,v pairs with keys listed in the fields_order list
    2) orders the dict fields (k,v pairs) based upon order of fields_order
    3) appends data if it is passed a k,v pair
    returns the result
    """
    payload = []
    for d in data:
        entity = dict([(f, d.get(f)) for f in fields_order])
        if append_data is not None:
            entity.update(append_data)
        payload.append(entity)
    return(payload)

def gp_exists(policies, newpolicy_name):
    policy_id = ''
    for policy in policies:
        if policy['name'] == newpolicy_name:
            policy_id = policy['groupPolicyId']
        
    return policy_id
 

print(f'\nGetting all orgs and associated networks for given API key. (This step may take some time)\n')

all_networks = []
for org in api_session.get_orgs():
    org_name = org['name']
    org_networks = api_session.get_networks(org['id'])

    for network in org_networks:
        network_name = network['name']

        if network:
            print(f'Getting data for Network: { network_name } in Org: { org_name }')
            dict1 = create_dict(data=[network], fields_order=['id','organizationId','name','tags'], append_data={'orgName': org_name})
            dict2 = create_dict(data=dict1, fields_order=['orgName', 'organizationId', 'name', 'id','tags'])
            all_networks.append(dict2[0])

target_networks = [
    network for network in all_networks if gp_networktag in network['tags']
]

print(f'\nThe following networks will be targeted based upon matching the tag "{ gp_networktag }":\n')
for network in target_networks:
    network_name = network['name']
    print(f'{ network_name } in org { org_name }')

input("\n\nPress Enter to continue...\n")

target_policies = []

for network in target_networks:
    network_id = network['id']
    network_name = network['name']
    policies = api_session.get_policies(networkid=network_id)

    if not policies:
        print(f'No group policies found in network: { network_name }.')
        print(f'Creating policy: { empty_policyname } in network: { network_name }.')
        create_policy = api_session.create_policy(networkid=network_id, policy_name=empty_policyname)

        target_policies.append({'network_id': network_id, 'network_name': network_name, 'policy_id': create_policy['groupPolicyId'], 'policy_name': empty_policyname})

    else:
        policy_id = gp_exists(policies=policies, newpolicy_name=empty_policyname)

        if policy_id:
            print(f'Policy name { empty_policyname } was already found in network { network_name }. '
            + f'Skipping policy creation for network { network_name }'
            )
            target_policies.append({'network_id': network_id, 'network_name': network_name, 'policy_id': policy_id, 'policy_name': empty_policyname})
        else:
            print(f'Creating policy: { empty_policyname } in network: { network_name }.')
            create_policy = api_session.create_policy(networkid=network_id, policy_name=empty_policyname)

            target_policies.append({'network_id': network_id, 'network_name': network_name, 'policy_id': create_policy['groupPolicyId'], 'policy_name': empty_policyname})

print(f'\nGroup policies created, reading mac addresses from csv file: { csv_file }\n')
print(f'Constructing client provisioning list (MACs)\n')

input_file, total_rows = csv_tools.read_csv(csv_file, ['MAC address','Description'])

clients = []

for index, item in enumerate(input_file, start=1):
    mac_address = item['macaddress']
    client_description = item['description']
    if not csv_tools.is_validmac(mac_address):
        print(f'***Note: MAC address: "{ mac_address }" on csv file: "{ csv_file }" row { (index+1) } is not a valid MAC address.***\n'
                + f'***Please correct and re-run the script or add this client manually.***\n'
            )
    elif mac_address == client_description:
        client_description = mac_address
    else:
        current_client = {
        'mac': mac_address,
        'name': client_description
        }
        clients.append(current_client)

print(f'\nProvisioning clients for each network and associating clients with policy: "{ empty_policyname }"\n')

current_policy = 0
successful_policies = 0
error_networks = []
for policy in target_policies:
    total_policies = len(target_policies)
    network_name = policy['network_name']
    current_policy += 1

    print(f'Provisioning clients for current network: "{ network_name }" (Policy #{ current_policy } of { total_policies })')

    try:
        api_session.provision_client(networkid=policy['network_id'], clients=clients, policy_id=policy['policy_id'])
        successful_policies += 1
    except api_session.APIError as e:
        error_networks.append[network_name]
        continue
    except Exception as e:
        print(f'Non meraki error: {e}')
        error_networks.append[network_name]
        continue

print(f'\n\nScript complete! { successful_policies } of { total_policies } networks had clients successfully provisioned and associated!\n\n')

if error_networks:
    print(f'The following networks had errors with policy/client provisioning:')
    for network in error_networks:
        print('network')
