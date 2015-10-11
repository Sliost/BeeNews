# coding=utf-8

import sys
import json
import argparse
import requests

import os
import os.path as osp
if __name__ == '__main__':
    # Make imports work
    sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
    os.chdir(osp.dirname(osp.dirname(osp.abspath(__file__))))
    import codecs
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)


def make_parser():
    parser = argparse.ArgumentParser(description='Import from all source to mongoDB.')
    parser.add_argument(
        '--version',
        help='Version of the program',
        action='version',
        version='import_articles 0.0'
    )

    parser.add_argument(
        '-i', '--input',
        type=str,
        default=None,
        help='The input from where the source will be taken'
    )

    parser.add_argument(
        '-t', '--type',
        type=int,
        default=0,
        help='The type of the input: 0 for file, 1 for an api'
    )

    parser.add_argument(
        '-a', '--api',
        type=str,
        default="http://localhost:5000",
        help='Host of the API (Default is localhost:5000)'
    )

    parser.add_argument(
        '-u', '--user',
        type=str,
        default='ladotevi@enseirb-matmeca.fr',
        help='The email of the user'
    )

    parser.add_argument(
        '--token',
        type=str,
        required=True,
        help='The token of the user'
    )

    return parser

from some_utils import SomeUtils

def reformat(inpt, inp_type, username):
    format_list = []

    if inp_type == 1:
        reader = inpt
    else:
        reader = open(inpt)

    for line in reader:
        item = json.loads(SomeUtils.to_unicode(line))
        item['username'] = username
        format_list.append(item)

    return format_list

def start_request(fp, host, inp_type, username, token):
    headers = {'Content-Type': 'application/json',
               'X-BeenewsAPI-Token': token}

    url = host + "/add"
    elements = reformat(fp, inp_type, username)

    for element in elements:
        data = json.dumps(element)
        r = requests.post(url=url, data=data, headers=headers)
        print r.text

# -------------------------------------------------------- MAIN ------------------------------------------------------ #

if __name__ == '__main__':
    the_parser = make_parser()
    the_args = the_parser.parse_args()

    if the_args.type == 0:
        if the_args.input is not None:
            start_request(the_args.input, the_args.api, the_args.type, the_args.user, the_args.token)
        else:
            print "Please choose an input"
    else:
        print "Not taking from APIs yet"
