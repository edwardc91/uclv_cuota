#!/usr/bin/python

import requests
from argparse import ArgumentParser
from time import sleep
from datetime import date
from os import system
import curses
from threading import *

__author__ = 'eduardo'


def init_curses():
    stdscr = curses.initscr()
    # curses.noecho()
    curses.curs_set(0)
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
    curses.init_pair(5, curses.COLOR_YELLOW, -1)


def end_curses(stdscr):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()


def curses_main_screen_init(stdscr, user):
    screen = stdscr.subwin(23, 79, 0, 0)
    screen.box()
    screen.addstr(1, 5, "Last seven days record for user ", curses.A_BOLD)

    screen.addstr(1, 37, user, curses.color_pair(2))
    screen.addstr(22, 50, "Press \"Ctrl+C\" to exit", curses.A_BOLD)
    screen.refresh()
    return screen


def curses_init_quote_window(stdscr):
    quote_window = stdscr.subwin(11, 60, 3, 8)
    quote_window.box()
    quote_window.refresh()
    return quote_window


def curses_init_totals_window(stdscr):
    totals_window = stdscr.subwin(4, 60, 14, 8)
    totals_window.box()
    totals_window.refresh()
    return totals_window


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


def update_text_show(screen):
    screen.addstr(20, 2, "Updating", curses.A_BOLD)
    i = 1
    while True:
        if i != 4:
            screen.addch(20, 10 + i, ".", curses.A_BOLD)
        else:
            screen.delch(20, 13)
            screen.delch(20, 12)
            screen.delch(20, 11)
            i = 1
        sleep(3)


def update_quotes_windows(quote_window, totals_window, json_week, user_quote, total_month, total_week, int_day):
    json_dic = json_week[0]
    format_con = format_week_json(json_dic)

    if user_quote > total_week:
        string = "%.2f" % (user_quote - total_week)
        quote_window.addstr(1, 2, "You have left ")
        quote_window.addstr(1, 16, string, curses.color_pair(3))
        quote_window.addstr(1, 16 + len(string), " MB approximately")
    else:
        string = "%.2f" % (-1 * (user_quote - total_week))
        quote_window.addstr(1, 2, "You have run out you quote in ")
        quote_window.addstr(1, 32, string, curses.color_pair(4))
        quote_window.addstr(1, 32 + len(string), " MB approximately")

    string = "%d" % (format_con[0])
    quote_window.addstr(2, 2, "Today you has consumed ")
    quote_window.addstr(2, 25 + len(string), " MB approximately")
    if format_con[0] <= 50:
        quote_window.addstr(2, 25, string, curses.color_pair(3))
    else:
        quote_window.addstr(2, 25, string, curses.color_pair(4))

    days_index = 1
    line = 3
    while days_index < len(format_con):
        subs = int_day - days_index
        quote_window.addstr(line, 2, "The last ")
        day_string = get_real_weekday(subs)
        quote_window.addstr(line, 11, day_string, curses.color_pair(5))
        current_x_pos = 11 + len(day_string)
        quote_window.addstr(line, current_x_pos, " you consumed ")
        current_x_pos += 14
        day_consume = "%d" % (format_con[days_index])
        if format_con[days_index] <= 50:
            quote_window.addstr(line, current_x_pos, day_consume, curses.color_pair(3))
        else:
            quote_window.addstr(line, current_x_pos, day_consume, curses.color_pair(4))
        current_x_pos += len(day_consume)
        quote_window.addstr(line, current_x_pos, " MB approximately")
        days_index += 1
        line += 1

    quote_window.addstr(line, 2, "Tomorrow you will have ")
    tomorrow_quote = "%d" % (int(format_con[6]))
    quote_window.addstr(line, 25, tomorrow_quote)
    quote_window.addstr(line, 25 + len(tomorrow_quote), " MB approximately")

    totals_window.addstr(1, 3, "You has consumed in the week ")
    string_total_week = "%d" % total_week
    totals_window.addstr(1, 32 + len(string_total_week), " of ")
    string_user_quote = "%d" % user_quote
    totals_window.addstr(1, 36 + len(string_total_week), string_user_quote, curses.color_pair(5))
    totals_window.addstr(1, 36 + len(string_total_week) + len(string_user_quote), " MBs")

    if total_week <= user_quote:
        totals_window.addstr(1, 32, string_total_week, curses.color_pair(3))
    else:
        totals_window.addstr(1, 32, string_total_week, curses.color_pair(4))

    totals_window.addstr(2, 3, "You has consumed in the month ")
    string_total_month = "%d" % (total_month + user_quote)
    totals_window.addstr(2, 33 + len(string_total_month), " of ")
    string_user_quote = "%d" % (user_quote * 5)
    totals_window.addstr(2, 37 + len(string_total_month), string_user_quote, curses.color_pair(5))
    totals_window.addstr(2, 37 + len(string_total_month) + len(string_user_quote), " MBs")

    if total_month <= user_quote * 5:
        totals_window.addstr(2, 33, string_total_month, curses.color_pair(3))
    else:
        totals_window.addstr(2, 33, string_total_month, curses.color_pair(4))

    # if total_month <= user_quote * 5:
    #     cons = "%s%d%s" % (bcolors.OKGREEN, total_month + user_quote, bcolors.ENDC)
    # else:
    #     cons = "%s%d%s" % (bcolors.FAIL, total_month + user_quote, bcolors.ENDC)
    #
    # print "You has consumed in the month %s of %s%d%s MB" % (cons, bcolors.WARNING, user_quote * 5, bcolors.ENDC)

    quote_window.refresh()
    totals_window.refresh()


def connect_api(user, request_type, using_curses, quote_window):
    if request_type == "week":
        params = {'view': 'user_week', 'user': user}
        result = requests.get(url="http://api.uclv.edu.cu/sta", params=params)
    else:
        result = requests.get(url="http://api.uclv.edu.cu/user_proxy_quota/" + user)

    if result.status_code == requests.codes.ok:
        json = result.json()
        return json
    else:
        if not using_curses:
            print "Is not working right now"
            exit(0)
        else:
            quote_window.clear()
            quote_window.box()
            quote_window.addstr(5, 20, "Loading...", curses.A_BLINK)
            quote_window.refresh()


def main():
    argp = ArgumentParser(version="2.0",
                          description="Show the weekly consumption of UCLV internet quote",
                          epilog='Copyright 2017 Eduardo Miguel Hernandez under license GPL v3.0'
                          )

    argp.add_argument('-u', '--user', type=str, required=True, help="User to search", dest='user')

    args = argp.parse_args()
    user = args.user

    json_quote = connect_api(user, 'quote', False, None)
    if len(json_quote) == 0:
        print "The user " + user + " doesn't exists"
        exit(0)

    system("clear")

    stdscr = init_curses()
    screen = curses_main_screen_init(stdscr, user)
    quote_window = curses_init_quote_window(stdscr)
    totals_windows = curses_init_totals_window(stdscr)

    quote_window.addstr(5, 20, "Loading...", curses.A_BLINK)
    quote_window.refresh()

    try:
        while True:
            json_quote = connect_api(user, 'quote', True, quote_window)

            quote_dict = json_quote[0]
            int_day = date.today().weekday()
            user_quote = int(quote_dict['cuota']) / 1000000

            total_month = int(quote_dict['total30']) / 1000000
            total_week = float(quote_dict['total']) / 1000000
            json_week = connect_api(user, 'week', True, quote_window)

            quote_window.clear()
            quote_window.box()
            update_quotes_windows(quote_window, totals_windows, json_week, user_quote, total_month, total_week, int_day)
            # print_json_week_output(json_week, user_quote, total_month, total_week, int_day)
            sleep(5)

    except KeyboardInterrupt:
        pass
    end_curses(stdscr)


if __name__ == '__main__':
    main()
