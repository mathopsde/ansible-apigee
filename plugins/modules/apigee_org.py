from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
'''

EXAMPLES = r'''
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
import requests
import json
import pyapigee

def getServers(module):
    servers = {}
    url = 'http://'+ module.params['mgmtserver'] + ':' + module.params['mgmtport'] + '/v1/servers'
    auth = (module.params['adminuser'],module.params['adminpwd'])
    response = requests.get(url,auth=auth)
    servers_json = json.loads(response.text)
    for x in servers_json:
        servers[x['uUID']] = {'eIP': x['internalIP'], 'pod': x['pod'], 'type': x['type']}
    return servers

def getRouter(module):
    router = {}
    servers = getServers(module)
    for server in servers:
        if 'router' in servers[server]['type']:
            router[server] = servers[server]
    return router

def getMessageProcessor(module):
    mp = {}
    servers = getServers(module)
    for server in servers:
        if 'message-processor' in servers[server]['type']:
            mp[server] = servers[server]
    return mp

def run_module():
    
    module_args = dict(
        method=dict(type='str', choices=['http','https'],required=True),
        mode=dict(type='str', required=False, default='create'),
        adminuser=dict(type='str', required=True),
        adminpwd=dict(type='str', required=True),
        mgmtserver=dict(type='str', required=True),
        orgadmin=dict(type='str', required=True),
        org=dict(type='str', required=True),
        env=dict(type='str', required=True),
        mgmtport=dict(type='str', required=False, default='8080')

    )

    result = dict(
        changed=False,
        org='',
        env='',
        original_message='',
        message='',
        reponsecr='',
        reponseaspod='',
        reponseadmin='',
        status='',
        aspod_url=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)
    
    # local variables
    method = module.params['method']
    mode = module.params['mode']
    mgmtserver = module.params['mgmtserver']
    mgmtport = module.params['mgmtport']
    adminuser = module.params['adminuser']
    adminpwd = module.params['adminpwd']
    org = module.params['org']
    env = module.params['env']
    orgadmin = module.params['orgadmin']

    # init apigee object

    apigee = pyapigee.apigee(method,mgmtserver,mgmtport,adminuser,adminpwd)

    if mode == 'create':
        apigee.createOrg(org)
        apigee.associateOrg(org,'gateway')
        apigee.addEnv(org,env)
        apigee.addAdmin(org,orgadmin)
        apigee.addAnalytics(org,env)

    if mode == 'delete':
        envs = apigee.getEnv(org)
        response = apigee.disassociateOrg(org,'gateway')
        for env in envs:
            apigee.deleteEnv(org,env)
        apigee.deleteOrg(org)

    result['message'] = response.text

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    # if module.params['new']:
    #     result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    # if module.params['name'] == 'fail me':
    #     module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
