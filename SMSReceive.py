#!/usr/bin/python

from xml.dom.minidom import parseString
from SMSReceive_settings import GET_ONCALL_CONFIG_ARGS, DEBUG, TEST, LOG_FILE
import subprocess

class SMSReceive:
    inbound_number = None
    inbound_message = None
    allowed_number_list = None
    get_oncall_config_args = GET_ONCALL_CONFIG_ARGS
    debug = DEBUG
    test = TEST
    log_file = LOG_FILE

    def __init__(self, sms_xml):
        self.inbound_number, self.inbound_message = self.parse_xml(sms_xml)
        if self.debug:
            self.log("Inbound Number: %s" % self.inbound_number)
        if not self.test:
            numbers = self.get_oncall_config()
            if self.debug:
                self.log(numbers)

            if numbers:
                self.allowed_number_list = self.extract_allowed_numbers(numbers)
                if self.debug:
                    self.log("Allowed Numbers List: %s" % self.allowed_number_list)

                acl_passed = self.check_number_acl(
                        self.inbound_number, self.allowed_number_list)
                if self.debug:
                    self.log("ACL Passed %s" % acl_passed)
                if acl_passed:
                    self.write_to_log_file(self.inbound_message)
            else:
                print "Could not execute number generator"

    def get_oncall_config(self):
        try:
            p = subprocess.Popen(
                self.get_oncall_config_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        except OSError, e:
            ## SMS Number generator not found
            ## Set output to error message
            print self.get_oncall_config_args[0]
            return None

        output, errors = p.communicate()
        return output

    def parse_xml(self, sms_xml):
        dom = parseString(sms_xml)
        inbound_message = None
        try:
            inbound_number = dom.getElementsByTagName('SenderNumber')[0]\
                    .firstChild.nodeValue
            inbound_number = int(inbound_number[-10:])
        except IndexError:
            # No inbound number in payload
            inbound_number = None
        try:
            inbound_message = dom.getElementsByTagName('Message')[0]\
                    .firstChild.nodeValue
        except IndexError:
            # No inbound message in payload
            inbound_message = None
        return inbound_number, inbound_message

    def extract_allowed_numbers(self, number_list):
        tmp = []
        for number in number_list.splitlines():
            try:
                number = int(number[-10:])
                tmp.append(number)
            except (TypeError, ValueError):
                pass
        return tmp

    def write_to_log_file(self, message):
        fh = open(self.log_file, 'a')
        fh.write(message)
        fh.close()

    def check_number_acl(self, inbound_number, allowed_number_list):
        if inbound_number in allowed_number_list:
            return True
        else:
            return False
    def log(self, message):
        fh = open(self.log_file, 'a')
        fh.write("%s\n" % (message))
        fh.close()
