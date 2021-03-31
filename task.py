# -*- coding: cp1251 -*-
import re
import json
import subprocess
from urllib import request
from prettytable import PrettyTable

def get_args(count, info):
    as_number = info['org'].split()[0][2::]
    provider = " ".join(info['org'].split()[1::])
    return [f"{count}.", info['ip'], info['country'], as_number, provider]


def get_bogon_args(count, info):
    return [f"{count}.", info['ip'], '*', '*', '*']


def complete(text_data):
    return 'Трассировка завершена.' in text_data


def timed_out(text_data):
    return 'Превышен интервал ожидания запроса' in text_data


def beginning(text_data):
    return 'Трассировка маршрута' in text_data


def invalid_input(text_data):
    return 'Не удается разрешить' in text_data


def generate_table():
    table = PrettyTable()
    table.field_names = ["number", "ip", "country", "AS number", "provider"]
    return table


def get_ip_info(ip):
    return json.loads(request.urlopen('https://ipinfo.io/' + ip + '/json').read())


def trace_as(address, table):
    tracert_proc = subprocess.Popen(["tracert", address], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    number = 0

    for raw_line in iter(tracert_proc.stdout.readline, ''):
        line = raw_line.decode('cp866')
        ip = re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)

        if complete(line):
            print(table)
            return
        if invalid_input(line):
            print('invalid input')
            return
        if beginning(line):
            continue
        if timed_out(line):
            print('request timed out')
            continue
        if ip:
            number += 1
            print(f'{"".join(ip)}')
            info = get_ip_info(ip[0])
            if 'bogon' in info:
                table.add_row(get_bogon_args(number, info))
            else:
                table.add_row(get_args(number, info))


def main():
    address = input('Enter address: ')
    table = generate_table()
    trace_as(address, table)


if __name__ == '__main__':
    main()
