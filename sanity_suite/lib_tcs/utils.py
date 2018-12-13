from sanity_suite.conf_tcs.config import *
import json
import re

#def get_tconfig_file(argv):
#
#	config_file = "config"
#
#	try:
#		opts, args = getopt.getopt(argv[1:], 'c:', [])
#	except getopt.GetoptError:
#		sys.exit(2)
#
#	for opt, arg in opts:
#		if opt in ('-c',):
#			config_file = arg.split(".")[0]
#
#	return (config_file, args)

def do_pass(tc, func, cond = 1):
	tmp=func.split()
	tc_name=(tc.__class__.__name__[:16]+'.'+tmp[0])
	tc_result='unknown'
	if cond:
		logger.info(('%-60s %s' % (tc.__class__.__name__[:16]+'.'+ func[:44], 'pass')))
		tc_result='passed'
		assert(True)

	else:
		logger.info(('%-60s %s' % (tc.__class__.__name__[:16]+'.'+ func[:44], 'fail')))
		tc_result='failed'
		assert(False)
	tc_name="\n"+tc_name + (' : %s' % tc_result)
	with open("summary.txt", "a") as myfile:
		myfile.write(tc_name)
	myfile.close()

def do_skip(tc, func):
	logger.info(('%-60s %s' % (tc.__class__.__name__+':'+ func, 'skip')))

def caller():
	return '%s.%s' % (inspect.stack()[3][3], inspect.stack()[2][3])

class QAMixin(object):

	def assertEqual(self, a, b, x = None):
		if x is None:
			do_pass(self, '%s %s %s' % (caller(), a, b), a == b)
		else:
			do_pass(self, x, a == b)
		assert a==b

	def assertNotEqual(self, a, b, x = None):
		do_pass(self, '%s %s %s' % (caller(), a, b), a != b)
		assert a!=b

	def assertTrue(self, a, x = None):
		do_pass(self, '%s %s' % (caller(), a), a == True)
		assert a==True

	def assertFalse(self, a, x = None):
		do_pass(self, '%s %s' % (caller(), a), a == False)
		assert a==False

	def skipTest(self, s, x = None):
		do_skip(self, s)

class PIOAppliance(QAMixin, object):

	def __init__(self, app_ip = APPLIANCE_IP):
		self.app_ip = app_ip
		self.token = None
		cj = http.cookiejar.CookieJar()
		self.base_url = "https://%s/" % app_ip
		logger.debug("self.base_url: {}".format(self.base_url))
		# SSLContext was introduced in ssl module from python 2.7.9
		if sys.version_info >= (2, 7, 9):
			ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
		else:
			import OpenSSL.SSL as ossl
			ssl_context = ossl.Context(ssl.PROTOCOL_TLSv1)
	
		self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),\
												  urllib.request.HTTPSHandler(context=ssl_context))
		logger.debug("Successfully urllib.request.build_opener: {}".format(self.opener))

	def get_url(self, endpoint):
		new_url = self.base_url + endpoint
		logger.debug("get_url: {}".format(new_url))
		return new_url

	def login(self, username = APP_USERNAME, password = APP_PASSWORD):
		values = {
		   'username': username,
		   'password': password,
		}
		 # Convert to params
		url = self.get_url("api-token-auth")
		res = self.post(url, values)
		logger.debug("self.post(url, values): {}".format(res))
		self.assertEqual(res.getcode(), 200)
		res = json.loads(res.read().decode('utf-8'))
		logger.debug("json.loads(res.read()): {}".format(res))
		self.token = res['token']
		self.opener.addheaders = [('Authorization', 'Token %s' % res['token']),
								 ('Content-Type', 'application/json')]
		

	def logout(self):
		url = self.get_url("api-token-auth")
		##Commenting for now
		#res = self.delete(url)
		#logger.debug(url)
		#logger.debug(res.getcode())
		#assert(res.getcode()== 200)
		self.opener.addheaders = [('Authorization', '')]

	def get(self, url, values = {}):
		if len(list(values.keys())) > 0:
			params = urllib.parse.urlencode(values)
			url = url + "?%s" % params
		try:
			response = self.opener.open(url)
		except urllib.error.HTTPError as e:
			response = e
			pass

		return response

	def post(self, url, values):
		data = json.dumps(values)
		logger.debug("json.dumps(values): {}".format(data))
		request = urllib.request.Request(url, data=data.encode())
		logger.debug("urllib.request.Request(url, data=data.encode()): {}".format(request))
		request.add_header('Content-Type', 'application/json')
		try:
			#gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1) #SSLv23
			#context = ssl._create_unverified_context()
			response = self.opener.open(request)
			logger.debug("self.opener.open(request): {}".format(response))
		except urllib.error.HTTPError as resp:
			response = resp
		return response

	def put(self, url, values):
		data = urllib.parse.urlencode(values)
		request = urllib.request.Request(url, data=data)
		request.get_method = lambda: 'PUT'
		try:
			response = self.opener.open(request)
		except urllib.error.HTTPError as response:
			pass

		return response

	def delete(self, url, values=None):

		data = None
		
		if values is not None:
			data = urllib.parse.urlencode(values).encode('utf-8')

		request = urllib.request.Request(url, data=data)
		request.get_method = lambda: 'DELETE'
		try:
			response = self.opener.open(request)
		except urllib.error.HTTPError as resp:
			response = resp

		return response

	def get_vcenters(self):
		get_vcenter_url = self.get_url("/plugin")

		# self.pio.login()

		res = self.get(get_vcenter_url)
		data = json.loads(res.read().decode('utf-8'))
						  
		logger.debug(get_vcenter_url)
		logger.debug(data)

		self.assertEqual(res.getcode(), 200)

		return data['data']

	def get_clusters(self, values):
		get_cluster_url = self.get_url("/install/1")

		res = self.get(get_cluster_url, values)
		data = json.loads(res.read().decode('utf-8'))

		return data

	def install(self, values):
		install_url = self.get_url("/install/0")
		res = self.post(install_url, values)

		rc = res.getcode()

		if rc != 200:
			logger.error("Failed to install PIO vib on %s" % values)
			return False

		return True

	def uninstall(self, values):
		uninstall_url = self.get_url("/uninstall/0")
		res = self.post(uninstall_url, values)

		rc = res.getcode()

		if rc != 200:
			logger.error("Failed to uninstall PIO vib on %s" % values)
			return False

		return True

	def get_cluster_config(self, values):
		get_cluster_conf_url = self.get_url("/install/2")

		res = self.get(get_cluster_conf_url, values)

		rc = res.getcode()

		if rc != 200:
			logger.error("Failed to fetch config for cluster %s" % values['cluster_name'])
			return

		data = json.loads(res.read().decode('utf-8'))	

		return data['config']

	def configure_cluster(self, values):
		cluster_config_url = self.get_url("/install/1")

		res = self.post(cluster_config_url, values)

		rc = res.getcode()

		if rc != 200:
			logger.error("Failed to configure cluster %s" % values['cluster_name'])
			return False

		return True

	def register(self, values):
		register_plugin_url = self.get_url("/install/2")

		res = self.post(register_plugin_url, values)

		rc = res.getcode()

		if rc != 200:
			logger.error("Failed to register plugin on vCenter %s" % values['vcenter_id'])
			return False

		return True

	def unregister(self, values):
		unregister_plugin_url = self.get_url("/uninstall/1")

		res = self.post(unregister_plugin_url, values)

		rc = res.getcode()

		if rc != 200:
			logger.error("Failed to unregister plugin on vCenter %s" % values['vcenter_id'])
			return False

		return True

	def add_vcenter(self, values):
		vcenter_url = self.get_url("/plugin")

		res = self.post(vcenter_url, values)
		ret = res.read().decode('utf-8')
		rc = res.getcode()

		if rc != 201:
			logger.error("Failed to add vCenter: %s" % ret)
			return False

		return True

	def delete_vcenter(self, values):
		vcenter_url = self.get_url("/plugin")

		vc_id = None

		res = self.delete(vcenter_url, values)
		rc = res.getcode()

		if rc != 200:
			ret = json.loads(res.read())
			logger.error("Failed to delete vCenter: %s" % ret)
			return False

		return True

def generate_report():
	content = []
	total_tcs = -1
	failed_tcs = -1
	passed_tcs = -1
	skipped_tcs = -1
	tc_name = ''
	with open('summary.txt', 'r') as fp:        
		for line in fp:
			if( len(line.rstrip()) < 2 ):
				continue
			flag = False
			for item in content:
				if( line.rstrip() == item ):
					flag = True
					break
			if ( flag == True ):
				pass #print ("Item '%s' found in list"%line)
			else:
				content.append(line.rstrip())
	for i in content:
		total_tcs = total_tcs + 1
		tc_name =tc_name + "\n %s"%i
		if re.search("passed",i):
			passed_tcs = passed_tcs + 1
		elif re.search("failed",i):
			failed_tcs = failed_tcs + 1
		else:
		   skipped_tcs +=1
	summary ="\n\n\t\t------------------ Summary -------------------\n \
		\n\t\tTotal Ran test cases      : %d"%(total_tcs)+"\
		\n\t\tTotal Passed test cases   : %d"%((passed_tcs))+"\
		\n\t\tTotal Failed test cases   : %d"%(failed_tcs)+"\
		\n\t\tTotal Skiped test cases   : %d"%(skipped_tcs)
	print(summary)
	my_date = date.today()
	summary_rp = 'none'
	summary_dict = {
			"day" : [calendar.day_name[my_date.weekday()]],
			"total_tcs" : total_tcs,
			"failed_tcs" : failed_tcs,
			"passed_tcs" : passed_tcs,
			"skipped_tcs" : skipped_tcs
		}
	with open('summary.obj', 'rb') as obj:
		summary_rp = pickle.load(obj)
	
	with open('summary.obj', 'wb') as obj:
		if not summary_rp:
			pickle.dump(summary_dict, obj, protocol=pickle.HIGHEST_PROTOCOL)
		else:
			update_pikcle_obj(summary_rp, summary_dict, obj)
	if "Tuesday" in summary_rp['day'] or len(summary_rp['day']) > 6:
		send_mail(summary_rp)
		os.remove('summary.obj')
	os.remove('summary.txt')
	
def update_pikcle_obj(summary_rp, summary_dict, obj):
	summary_rp['day'].extend(summary_dict['day'])
	for key in summary_rp.keys():
		if key != 'day':
			if summary_dict[key] <= 0:
				summary_dict[key] = 0
			summary_rp[key] = summary_rp[key] + summary_dict[key]
	pickle.dump(summary_rp, obj, protocol=pickle.HIGHEST_PROTOCOL)
	
def send_mail(summary):
	logger.debug('Sending Mail of the Automation Summary')
	recievers = EMAIL_IDS
	email_id = "testlink@primaryio.com"
	subjt = 'Automation execution summary of Control Plane:' + \
			datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	body_msg =("\n\n\t\t------------------ Summary -------------------\n \
		\n\t\tTotal Automation Run on   : %s"%(summary['day'])+"\
		\n\t\tTotal Ran test cases      : %d"%(summary['total_tcs'])+"\
		\n\t\tTotal Passed test cases   : %d"%(summary['passed_tcs'])+"\
		\n\t\tTotal Failed test cases   : %d"%(summary['failed_tcs'])+"\
		\n\t\tTotal Skiped test cases   : %d"%(summary['skipped_tcs']))
	body = body_msg
	pwd = "admin@123"
	print("Sending email to users")
	try:
		for toaddr in recievers:
			fromaddr = email_id
			toaddr = toaddr
			msg = MIMEMultipart()
			msg['From'] = fromaddr
			msg['To'] = toaddr
			msg['Subject'] = subjt
			msg.attach(MIMEText(body, 'plain'))
	
			server = smtplib.SMTP('smtp.gmail.com', 587)                
			server.starttls()
			server.login(fromaddr, pwd)
			text = msg.as_string()
			server.sendmail(fromaddr, toaddr, text)
			server.quit()
	except smtplib.SMTPAuthenticationError:
		print("Error! Wrong email-id or password.")    
	except smtplib.SMTPConnectError:
		print('Connection Failed')
	print("mail sent to : %s"%recievers)
