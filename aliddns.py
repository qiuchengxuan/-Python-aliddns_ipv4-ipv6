#!/usr/bin/env python3

import json
from collections import namedtuple
from urllib.request import urlopen

from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import (
    DescribeDomainRecordsRequest
)
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from aliyunsdkcore.client import AcsClient
from jsonpath import jsonpath

ACCESS_KEY_ID = "ACCESS_KEY_ID"  # 将accessKeyId改成自己的accessKeyId
ACCESS_SECRET = "ACCESS_SECRET"  # 将accessSecret改成自己的accessSecret
DOMAIN = "qiubuyi.me"  # 你的主域名
RECORDS = [('*', 'A'), ('*', 'AAAA')]

client = AcsClient(ACCESS_KEY_ID, ACCESS_SECRET, 'cn-hangzhou')


def resolve_ipv4():
    data = json.loads(urlopen('http://ip-api.com/json/?fields=query').read())
    return data['query']


def resolve_ipv6():
    response = urlopen('https://api-ipv6.ip.sb/ip').read()
    return str(response, encoding='utf-8').strip()


def update(RecordId, RR, Type, Value):  # 修改域名解析记录
    request = UpdateDomainRecordRequest()
    request.set_accept_format('json')
    request.set_RecordId(RecordId)
    request.set_RR(RR)
    request.set_Type(Type)
    request.set_Value(Value)
    client.do_action_with_exception(request)


def add(RR, Type, Value):  # 添加新的域名解析记录
    request = AddDomainRecordRequest()
    request.set_accept_format('json')
    request.set_DomainName(DOMAIN)
    request.set_RR(RR)
    request.set_Type(Type)
    request.set_Value(Value)
    client.do_action_with_exception(request)


Record = namedtuple('Record', 'id value')


def get(name, record_type):
    request = DescribeDomainRecordsRequest()
    request.set_DomainName(DOMAIN)
    request.set_RRKeyWord(name)
    request.set_Type(record_type)
    text = client.do_action_with_exception(request)
    result = jsonpath(json.loads(text), '$.DomainRecords.Record[0]')
    if not result:
        return None
    return Record(result[0]['RecordId'], result[0]['Value'].strip())


def main():
    try:
        ipv4 = resolve_ipv4()
    except OSError:
        ipv4 = None
    try:
        ipv6 = resolve_ipv6()
    except OSError:
        ipv6 = None

    for (name, record_type) in RECORDS:
        print('Handling record %s type %s' % (name, record_type))

        new_value = ipv4 if record_type == 'A' else ipv6
        if new_value is None:
            print('Address not resolved')
            continue

        record = get(name, record_type)
        if record is None:
            print('Add non-exists record')
            add(name, record_type, new_value)
            continue

        print('Found record id %s' % record.id)
        if record.value != new_value:
            print('Update record with %s' % new_value)
            update(record.id, name, record_type, new_value)
        else:
            print('Nothing to do')


if __name__ == '__main__':
    try:
        main()
    except:
        pass
