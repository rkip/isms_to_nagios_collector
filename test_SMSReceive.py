#!/usr/bin/python
# The contents of this file are subject to the Mozilla Public License
# Version 1.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
# License for the specific language governing rights and limitations
# under the License.
#
# The Original Code is mozilla-nagios-bot
#
# The Initial Developer of the Original Code is Rob Tucker. Portions created
# by Rob Tucker are Copyright (C) Mozilla, Inc. All Rights Reserved.
#
# Alternatively, the contents of this file may be used under the terms of the
# GNU Public License, Version 2 (the "GPLv2 License"), in which case the
# provisions of GPLv2 License are applicable instead of those above. If you
# wish to allow use of your version of this file only under the terms of the
# GPLv2 License and not to allow others to use your version of this file under
# the MPL, indicate your decision by deleting the provisions above and replace
# them with the notice and other provisions required by the GPLv2 License. If
# you do not delete the provisions above, a recipient may use your version of
# this file under either the MPL or the GPLv2 License.

from mock import Mock
import unittest
import re
from SMSReceive import SMSReceive
from SMSReceive_settings import LOG_FILE
import os

"""
    Test example payload of message.
    Documentation here: http://www.multitech.com/en_US/DOCUMENTS/Families/MultiModemiSMS/manuals.aspx
"""

sms_payload = """<?xml version="1.0" encoding="ISO-8859-1"?>
<Response>
<MessageNotification>
<ModemNumber>2:19525945092</ModemNumber>
<SenderNumber>6754535645</SenderNumber>
<Date>08/03/10</Date>
<Time>09:05:30</Time>
<Message>Here is a test message</Message></MessageNotification>
</Response>"""

"""
    Random list of numbers to look like
    valid phone numbers for testing
    Including intl prefixes and 1 to area codes
"""

sms_numbers = """foo<||>6754535645
bar<||>1618275516
baz<||>+8286439827
yep<||>5619193759
nope<||>14614449451
outofnames<||>6977636366"""

class TestSMSReceive(unittest.TestCase):
    def setUp(self):
        self.sms = sms_payload
        self.sms_numbers = sms_numbers

    def test1_build_dom_object(self):
        sms = SMSReceive(self.sms)
        self.assertEqual(sms.inbound_number, 6754535645)
        self.assertEqual(sms.inbound_message, 'Here is a test message')

    def test2_test_number_extraction(self):
        sms = SMSReceive(self.sms)
        final_list = sms.extract_allowed_numbers(self.sms_numbers)
        self.assertEqual(final_list[0]['number'], 6754535645)
        self.assertEqual(final_list[1]['number'], 1618275516)
        self.assertEqual(final_list[2]['number'], 8286439827)

    def test3_write_to_file(self):
        try:
            os.remove(LOG_FILE)
        except OSError:
            # File does not exist
            pass
        self.assertFalse(os.path.exists(LOG_FILE))
        sms = SMSReceive(self.sms, self.sms_numbers)
        self.assertTrue(os.path.exists(LOG_FILE))
        lines = open(LOG_FILE, 'r').readlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], 'foo<||>Here is a test message')

    def test4_number_acl_valid(self):
        sms = SMSReceive(self.sms, self.sms_numbers)
        sms_number_list = sms.extract_allowed_numbers(self.sms_numbers)
        self.assertEqual(sms.check_number_acl(6754535645, sms_number_list), True)

    def test5_number_acl_invalid(self):
        sms = SMSReceive(self.sms, self.sms_numbers)
        sms_number_list = sms.extract_allowed_numbers(self.sms_numbers)
        self.assertEqual(sms.check_number_acl(9992345109, sms_number_list), False)

    def test6_get_name_by_number(self):
        sms = SMSReceive(self.sms, self.sms_numbers)
        sms_number_list = sms.extract_allowed_numbers(self.sms_numbers)
        self.assertEqual(sms.get_name_by_number(sms_number_list,6754535645), 'foo')

