#!/usr/bin/env python3

from quopri import decodestring, encodestring
import sqlite3
import json
from datetime import datetime


class Contact:
    def __init__(self):
        contact = None
        vcard = None

    def init(self, data):
        self.contact = {
            'Fn': data['FirstName'],
            'Ln': data['LastName'],
            'Mn': data['MiddleName'],
            'BD': datetime.fromtimestamp(
                int(data['BDay'])).strftime('%Y-%m-%d'),
            'Nick': data['Nickname'],
            'Email': data['Email'],
            'Tel': data['Tel'],
            'Url': data['Url']
        }

    def gen_vcard(self, vtype=3):
        vcard_data = str()
        vcard_data += 'BEGIN:VCARD\n'

        if vtype == 3:
            version = '3.0'
        elif vtype == 2.1:
            version = '2.1'
        vcard_data += 'VERSION:%s\n' % version

        vcard_data += 'N;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:%s\n' % \
            encodestring(str('%s;%s;%s' % (
                self.contact['Ln'],
                self.contact['Fn'],
                self.contact['Mn'],)).encode()).decode('utf-8')

        tel_list = json.loads('{%s}' % self.contact['Tel'])
        for tel_type in tel_list:
            for tel in tel_list[tel_type]:
                vcard_data += 'TEL;%s:%s\n' % (tel_type.upper(), tel,)

        vcard_data += 'NICKNAME:%s\n' % self.contact['Nick']

        if vtype == 3:
            for nickname in json.loads('%s' % self.contact['Email']):
                vcard_data += 'EMAIL:%s\n' % \
                    encodestring(nickname.encode()).decode('utf-8')
        elif vtype == 2.1:
            vcard_data += 'EMAIL:%s\n' % \
                json.loads('%s' % self.contact['Email'])[0]

        for url in json.loads('%s' % self.contact['Url']):
            vcard_data += 'URL:%s\n' % url

        if vtype == 3:
            vcard_data += 'BDAY:%s\n' % self.contact['BD']
        elif vtype == 2.1:
            vcard_data += 'BDAY:%s\n' % ''.join(self.contact['BD'].split('-'))

        vcard_data += 'REV:%s\n' % datetime.fromtimestamp(
            datetime.timestamp(datetime.now())).strftime('%Y%m%d')
        vcard_data += 'END:VCARD\n'

        self.vcard = vcard_data

    def get_name(self):
        return('%s %s %s' % (
            self.contact['Ln'],
            self.contact['Fn'],
            self.contact['Mn']))

    def save(self, filename, vtype=3):
        self.gen_vcard(vtype=vtype)

        with open('./vcf/%s.vcf' % filename, 'w', encoding='utf-8') as f:
            f.write(self.vcard)

db_con = sqlite3.connect('db.sqlite3')
db_con.row_factory = sqlite3.Row
db_cur = db_con.cursor()
db_cur.execute('SELECT * FROM contacts')

if __name__ == '__main__':
    for row in db_cur.fetchall():
        contact = Contact()
        contact.init(row)

        print('Saving: %s' % contact.get_name(), end='\r')
        contact.save(contact.get_name())
