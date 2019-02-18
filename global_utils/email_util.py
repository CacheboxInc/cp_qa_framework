import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import strftime, gmtime

def send_mail(link,email_id):
	print('Sending eMail')
	recievers = email_id
	email_id = "testlink@primaryio.com"
	subjt = 'Automation execution summary of Control Plane:' + \
			strftime("%Y%m%d%H%M", gmtime())

	body_msg =("\n\n\t\tTest run result \n \
		\n\t\tTotal Skiped test cases   : %s"%(link))
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
