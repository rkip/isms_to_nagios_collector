#!/usr/bin/python
import cgi, cgitb 
from SMSReceive import SMSReceive

# Create instance of FieldStorage 
form = cgi.FieldStorage() 
form_data = form.getvalue('XMLDATA')
sms = SMSReceive(form_data)
print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title>SMS Receiver</title>"
print "</head>"
print "<body>"
print "<h2>SMS Receiver</h2>"
print "</body>"
print "</html>"
