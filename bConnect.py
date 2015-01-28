import re
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

    def get_jobs_with_error(self):

        #to define this you need to find the error messages in your language.
        #see get_unique_status_text() method to find out whats your StateText to match
        ERR_DEF = [
            'Fehler',
            'keine Verbindung',
            'rungstimeout',
            'fehlgeschlagen',
            'keine ausf',
            'nicht gestartet',
            'schlugen fehl',
        ]

        data = self.connect(self.bms_job_instances_url)
        jobs_with_err=[]

        for n in data:
            for x in ERR_DEF:
                if x in n['StateText']:
                    jobs_with_err.append(n)

        return json.dumps(jobs_with_err)

    def get_job_error_count(self):

        return len(json.loads(self.get_jobs_with_error()))


    def get_jobs(self):

        return self.connect(self.bms_job_instances_url)

    def get_jobs_by_state(self,state_id):
        #See bConnect.pdf from baramundi documentation:
        # [BmsNetState]
        # -1 Unknown
        # 0 Assigned
        # 1 Running
        # 2 FinishedSuccess
        # 3 FinishedError
        # 4 FinishedCanceled
        # 5 ReScheduled
        # 6 ReScheduledError
        # 7 WaitingForUser
        # 8 RequirementsNotMet
        # 9 Downloading

        data = self.connect(self.bms_job_instances_url)
        jobs_running =[]

        for n in data:
            if int(n['BmsNetState']) ==state_id:
                jobs_running.append(n)

        return json.dumps(jobs_running)

    def get_jobs_running_count(self):

        return len(json.loads(self.get_jobs_by_state(1)))


    def get_jobs_scheduled(self):

        return self.get_jobs_by_state(5)

    def get_jobs_scheduled_count(self):

        return len(json.loads(self.get_jobs_scheduled()))


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

        #old version
        # data = self.connect(self.bms_job_instances_url)
        # x = []
        #
        # for n in data:
        #     if id in n['EndpointId']:
        #         x.append(n)
        #
        # return json.dumps(x)

        #new in 2014 R2
        return self.connect(self.bms_job_instances_url+'?endpointid=%s'%id)

    def get_client_count(self):

        return len(self.connect(self.bms_endpoints_url))

    def get_client_count_active(self):

        return len(json.loads(self.get_clients_active()))

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

        return json.dumps(active_clients)

    def get_clients_inactive(self):

        #We've defined an extra variable with "Deaktiviert"
        #To use that method, you have to define this or simliar too
        #
        inactive_string = 'Deaktiviert'

        return self.connect(self.bms_search_url+'?type=endpoint&term=%s' %inactive_string)

    def get_clients_from_keyword(self,keyword): #You can search mostly everything with this method

            return self.connect(self.bms_search_url+'?type=endpoint&term=%s' %keyword)




    #Help methods

    def get_unique_status_text(self):
        re1 = '((?:(?:[0-2]?\\d{1})|(?:[3][01]{1}))[-:\\/.](?:[0]?[1-9]|[1][012])[-:\\/.](?:(?:[1]{1}\\d{1}\\d{1}\\d{1})|(?:[2]{1}\\d{3})))(?![\\d])'	# DDMMYYYY 1
        re2 = '.*?'	# Non-greedy match on filler
        re3 = '((?:(?:[0-1][0-9])|(?:[2][0-3])|(?:[0-9])):(?:[0-5][0-9])(?::[0-5][0-9])?(?:\\s?(?:am|AM|pm|PM))?)'	# HourMinuteSec 1
        re4 = '.*?'	# Non-greedy match on filler
        re5 = '((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))(?![\\d])'	# IPv4 IP Address 1
        rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)


        x=[]
        for n in self.get_jobs():
            if re.sub(re5,'',re.sub(rg,'',n['StateText'])) not in x:
                x.append(re.sub(re5,'',re.sub(rg,'',n['StateText'])))

        return x







