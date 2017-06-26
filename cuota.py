#!/usr/bin/python

import requests
from argparse import ArgumentParser
from time import sleep
from datetime import date
from os import system

__author__ = 'eduardo'


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_real_weekday(index):
    list_real_weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return list_real_weekday[index]


def format_week_json(json_dic):
    result = []
    index = 0
    while index < 7:
        unformat_con = json_dic['day' + str(index)]
        result.append(int(unformat_con) / 1000000)
        index += 1

    return result


def print_json_week_output(json_week, user_quote, total_month, total_week, int_day):
    json_dic = json_week[0]
    format_con = format_week_json(json_dic)
    print "Last seven days record for user %s%s%s:" % (bcolors.OKBLUE, json_dic['usuario'], bcolors.ENDC)

    if user_quote > total_week:
        print "You have left %s%.2f%s MB approximately" % (bcolors.OKGREEN, user_quote - total_week, bcolors.ENDC)
    else:
        print "You have run out you quote in %s%.2f%s MB approximately" % (
            bcolors.FAIL, -1 * (user_quote - total_week), bcolors.ENDC)

    today = ""
    if format_con[0] <= 50:
        today = "%s%d%s" % (bcolors.OKGREEN, format_con[0], bcolors.ENDC)
    else:
        today = "%s%d%s" % (bcolors.WARNING, format_con[0], bcolors.ENDC)

    print "Today you has consumed %s MB approximately" % today

    index = 1
    while index < len(format_con):
        subs = int_day - index
        if format_con[index] <= 50:
            print "The last %s%s%s you consumed %s%d%s MB approximately" % (bcolors.WARNING,
                                                                            get_real_weekday(subs), bcolors.ENDC,
                                                                            bcolors.OKGREEN, format_con[index],
                                                                            bcolors.ENDC)
        else:
            print "The last %s%s%s you consumed %s%d%s MB approximately" % (bcolors.WARNING,
                                                                            get_real_weekday(subs), bcolors.ENDC,
                                                                            bcolors.FAIL, format_con[index],
                                                                            bcolors.ENDC)
        index += 1

    print "Tomorrow you will have %d MB approximately" % (int(format_con[6]))

    cons = ""
    if total_week <= user_quote:
        cons = "%s%d%s" % (bcolors.OKGREEN, total_week, bcolors.ENDC)
    else:
        cons = "%s%d%s" % (bcolors.FAIL, total_week, bcolors.ENDC)

    print "You has consumed in the week %s of %s%d%s MB" % (cons, bcolors.WARNING, user_quote, bcolors.ENDC)

    if total_month <= user_quote * 5:
        cons = "%s%d%s" % (bcolors.OKGREEN, total_month + user_quote, bcolors.ENDC)
    else:
        cons = "%s%d%s" % (bcolors.FAIL, total_month + user_quote, bcolors.ENDC)

    print "You has consumed in the month %s of %s%d%s MB" % (cons, bcolors.WARNING, user_quote * 5, bcolors.ENDC)
    print bcolors.BOLD + "Press \"Ctrl+C\" to exit" +bcolors.ENDC


def connect_api(user, request_type):
    if request_type == "week":
        params = {'view': 'user_week', 'user': user}
        result = requests.get(url="http://api.uclv.edu.cu/sta", params=params)
    else:
        result = requests.get(url="http://api.uclv.edu.cu/user_proxy_quota/" + user)

    if result.status_code == requests.codes.ok:
        json = result.json()
        return json
    else:
        print bcolors.FAIL + "Is not working right now" + bcolors.ENDC
        exit(0)


def main():
    argp = ArgumentParser(version="2.0",
                          description="Show the weekly consumption of UCLV internet quote",
                          epilog='Copyright 2017 Eduardo Miguel Hernandez under license GPL v3.0'
                          )

    argp.add_argument('-u', '--user', type=str, required=True, help="User to search", dest='user')

    args = argp.parse_args()
    user = args.user

    # init(autoreset=True)

    system("clear")
    try:
        while True:
            json_quote = connect_api(user, 'quote')

            if len(json_quote) == 0:
                print "The user " + bcolors.WARNING + user + bcolors.ENDC + " doesn't exists"
                exit(0)

            quote_dict = json_quote[0]
            int_day = date.today().weekday()
            user_quote = int(quote_dict['cuota']) / 1000000

            total_month = int(quote_dict['total30']) / 1000000
            total_week = float(quote_dict['total']) / 1000000
            json_week = connect_api(user, 'week')
            print_json_week_output(json_week, user_quote, total_month, total_week, int_day)
            sleep(5)
            system("clear")
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
