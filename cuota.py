#!/usr/bin/python

import requests
from argparse import ArgumentParser
from time import sleep
from datetime import date
from os import system
import curses

__author__ = 'eduardo'


def init_curses():
    stdscr = curses.initscr()
    # curses.noecho()
    curses.cbreak()
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses_init_pairs()
    return stdscr


def curses_init_pairs():
    curses.init_pair(2, curses.COLOR_BLUE, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.init_pair(4, curses.COLOR_RED, -1)


def end_curses(stdscr):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()


def curses_main_screen_init(stdscr, user):
    screen = stdscr.subwin(23, 79, 0, 0)
    screen.box()
    screen.addstr(1, 2, "Last seven days record for user ")

    screen.addstr(1, 34, user, curses.color_pair(2))
    screen.refresh()
    return screen


def curses_init_quote_window(stdscr):
    quote_window = stdscr.subwin(15, 60, 3, 1)
    quote_window.box()
    quote_window.refresh()
    return quote_window


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


def update_quotes_windows(quote_window, json_week, user_quote, total_month, total_week, int_day):
    json_dic = json_week[0]
    format_con = format_week_json(json_dic)

    if user_quote > total_week:
        string = "%.2f" % (user_quote - total_week)
        quote_window.addstr(1, 1, "You have left ")
        quote_window.addstr(1, 15, string, curses.color_pair(3))
        quote_window.addstr(1, 15 + len(string), " MB approximately")
    else:
        string = "%.2f" % (-1 * (user_quote - total_week))
        quote_window.addstr(1, 1, "You have run out you quote in ")
        quote_window.addstr(1, 31, string, curses.color_pair(4))
        quote_window.addstr(1, 31 + len(string), " MB approximately")

    string = "%d" % (format_con[0])
    quote_window.addstr(2, 1, "Today you has consumed ")
    quote_window.addstr(2, 24 + len(string), " MB approximately")
    if format_con[0] <= 50:
        quote_window.addstr(2, 24, string, curses.color_pair(3))
    else:
        quote_window.addstr(2, 24, string, curses.color_pair(4))

    quote_window.refresh()


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
    print bcolors.BOLD + "Press \"Ctrl+C\" to exit" + bcolors.ENDC


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
        print "Is not working right now"
        exit(0)


def main():
    argp = ArgumentParser(version="2.0",
                          description="Show the weekly consumption of UCLV internet quote",
                          epilog='Copyright 2017 Eduardo Miguel Hernandez under license GPL v3.0'
                          )

    argp.add_argument('-u', '--user', type=str, required=True, help="User to search", dest='user')

    args = argp.parse_args()
    user = args.user

    json_quote = connect_api(user, 'quote')
    if len(json_quote) == 0:
        print "The user " + user + " doesn't exists"
        exit(0)

    system("clear")

    stdscr = init_curses()
    screen = curses_main_screen_init(stdscr, user)
    quote_window = curses_init_quote_window(stdscr)

    try:
        while True:
            json_quote = connect_api(user, 'quote')

            quote_dict = json_quote[0]
            int_day = date.today().weekday()
            user_quote = int(quote_dict['cuota']) / 1000000

            total_month = int(quote_dict['total30']) / 1000000
            total_week = float(quote_dict['total']) / 1000000
            json_week = connect_api(user, 'week')

            update_quotes_windows(quote_window, json_week, user_quote, total_month, total_week, int_day)
            # print_json_week_output(json_week, user_quote, total_month, total_week, int_day)
            sleep(5)

    except KeyboardInterrupt:
        pass
    end_curses(stdscr)


if __name__ == '__main__':
    main()
