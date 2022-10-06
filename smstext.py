from datetime import date, timedelta

import sys, getopt

from twilio.rest import Client
import json


def build_message(name, group, alert_type, due_date):
    group_names = ''
    for m in group:
        group_names += m['name'] + ', '
    return f'FAB{name}!!!!, your {alert_type} for your FAB weekly is due on {due_date}. In case you\'ve forgotten, ' \
           f'your group is {group_names}make a group chat! Please text Elliot, if you have any questions! Here are ' \
           f'some important links:\n' \
           f'Guidelines - https://tinyurl.com/3af3y4km\n' \
           f'Canva Template - https://tinyurl.com/2ku6unvu\n'


def send_sms(client, messaging_service_sid, body, to, test=False):
    print(f"Sending message to {to}:\n{body}")
    if not test:
        message = client.messages.create(
            messaging_service_sid=messaging_service_sid,
            body=body,
            to=to
        )
        print(message.sid)


def generate_reminder_dates(today, num_days, interval):
    dates = [today.strftime("%m/%d/%Y")] * (num_days + 1)
    for i in range(num_days):
        dates[i+1] = (today + timedelta(days=(i + 1) * interval)).strftime("%m/%d/%Y")
    return dates


def main(test=False, text_all=False):
    secrets = json.loads(open('twillo.json').read())
    account_sid = secrets['account_sid']
    auth_token = secrets['auth_token']
    client = Client(account_sid, auth_token)

    today = date.today()
    dates = generate_reminder_dates(today, 2, 2)

    groups = json.loads(open('groups.json').read())
    texts = json.loads(open('texts.json').read())
    admins = json.loads(open('admins.json').read())

    texts_sent = 0
    recipients = ""

    if text_all:
        for group in groups:
            for member in groups[group]:
                send_sms(client, secrets['messaging_service_sid'],
                         f"What up FAB{member['name']}! This is a test message from the bot of doom.",
                         member['number'], test)
                texts_sent += 1
                recipients += member['name'] + ", "
    else:
        due = None
        for day in dates:
            if day in texts:
                due = day
                break
        if due is not None:
            for group_alert in texts[due]:
                for member in groups[group_alert['group-id']]:
                    message = build_message(member['name'], groups[group_alert['group-id']], group_alert['alert-type'], due)
                    send_sms(client, secrets['messaging_service_sid'], message, member['number'], test=test)
                    texts_sent += 1
                    recipients += member['name'] + ", "
    if texts_sent > 0:
        admin_report = f"Admin Report: {texts_sent} messages sent. Recipients {recipients[:-2]}."
        print(admin_report)
        for admin in admins["admins"]:
            send_sms(client, secrets['messaging_service_sid'], admin_report, admin["number"], test=test)


if __name__ == '__main__':
    argv = sys.argv[1:]
    test = False
    text_all = False
    try:
        opts, args = getopt.getopt(argv, "ta", [])
    except getopt.GetoptError:
        print('smstext.py -t')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-t':
            test = True
            print('In testing mode, no texts will be sent, but the message will be printed to the console')
        elif opt == '-a':
            text_all = True
            print('In all mode, all messages will be sent')
    main(test, text_all)
