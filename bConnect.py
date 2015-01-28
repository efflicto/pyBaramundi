import urllib2
import json
import base64


class BConnect:
    def __init__(self, bms, port, user_name, password):
        self.bms = bms
        self.user_name = user_name
        self.password = password
        self.port = port

        self.bms_jobs_url = 'https://%s:%s/bConnect/v1.0/jobs.json' % (self.bms,self.port)
        self.bms_job_instances_url = 'https://%s/bConnect/v1.0/jobinstances.json' % self.bms
        self.bms_endpoints_url = 'https://%s/bConnect/v1.0/endpoints.json' % self.bms
        self.bms_info_url = 'https://%s:%s/bConnect/info.json' % (self.bms,self.port)
        self.bms_software_scan_rules_url = 'https://%s/bConnect/v1.0/softwarescanrules.xml' % self.bms
        self.bms_endpoint_inv_software_url = 'https://%s/bConnect/v1.0/softwarescanrules.xml' % self.bms
        self.bms_search_url = 'https://%s/bConnect/v1.0/search.json' % self.bms

    def connect(self, url):

        request = urllib2.Request(url)

        base64string = base64.encodestring('%s:%s' % (self.user_name, self.password)).replace('\n', '')
        request.add_header('Authorization', 'Basic %s' % base64string)

        result = urllib2.urlopen(request).read()

        return json.loads(result)

        pass

    def test_connection(self):

        if 'baramundi software AG' in self.connect(self.bms_info_url)['Company']:
            return True
        else:
            return False

    # ##Job methods

    def get_job_instance_ids(self):

        data = self.connect(self.bms_job_instances_url)
        instance_ids = []

        for n in data:
            instance_ids.append(n['Id'])

        return instance_ids

    def get_job_instance_infos(self, id):

        data = self.connect(self.bms_job_instances_url)

        for n in data:
            if id in n['Id']:
                x = n
                break

        return x

    def get_jobs_from_keyword(self,keyword):

        return self.connect(self.bms_search_url+'?type=job&term=%s' % keyword)





    ###Client methods

    def get_client_ids(self):

        data = self.connect(self.bms_endpoints_url)
        x = []

        for n in data:
            x.append(n['Id'])

        return x


    def get_client_info(self, id):

        return self.connect(self.bms_endpoints_url + '?id=' + id)


    def get_client_name(self, id):

        return self.connect(self.bms_endpoints_url + '?id=' + id)['HostName']

    def get_client_id_by_name(self, client_name):

        data = self.connect(self.bms_endpoints_url)

        for n in data:
            if client_name.lower() in n['HostName'].lower():
                x = n['Id']
                break

        return x

    def get_client_jobs(self, id):

        data = self.connect(self.bms_job_instances_url)
        x = []

        for n in data:
            if id in n['EndpointId']:
                x.append(n)

        return json.dumps(x)

    def get_client_count(self):

        return len(self.connect(self.bms_endpoints_url))

    def get_client_count_active(self):

        return len(self.get_clients_active())

    def get_client_count_inactive(self):

        return len(self.get_clients_inactive())

    def get_clients_active(self):

        all_clients = self.connect(self.bms_endpoints_url)
        inactive_clients = self.get_clients_inactive() #Please look at the comment from this method
        active_clients = []
        inactive_client_ids =[]

        for n in inactive_clients:
            inactive_client_ids.append(n['Id'])

        for n in all_clients:
            if n['Id'] not in inactive_client_ids:
                active_clients.append(n)

        return active_clients

    def get_clients_inactive(self):

        #We've defined an extra variable with "Deaktiviert"
        #To use that method, you have to define this or simliar too
        #
        inactive_string = 'Deaktiviert'

        return self.connect(self.bms_search_url+'?type=endpoint&term=%s' %inactive_string)

    def get_clients_from_keyword(self,keyword): #You can search mostly everything with this method

            return self.connect(self.bms_search_url+'?type=endpoint&term=%s' %keyword)







