#!/usr/bin/env python
# coding: utf-8

import sys
import os
import requests
import argparse
import subprocess
import time

NVIDIA_URL = 'https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3090/'

def get_env(name, prompt):
    value = os.environ.get(name)
    if value == "":
        value = input(prompt)
    return value


def send_notification(domain, api, to, subject, body):
    mailgun_url = "https://api.mailgun.net/v3/%s/messages" % domain
    mailgun_from = "Nvidia Dog <dog@%s>" % domain
    return requests.post(
        mailgun_url,
        auth=("api", api),
        data={"from": mailgun_from,
              "to": [to],
              "subject": subject,
              "text": body})


def run_loop(domain, api, to):
    send_notification(domain, api, to, "Nvidia RTX 3090 daemon", "Started!")
    while True:
        try:
            headers = {"Accept-Language": "en-US,en;q=0.5"}
            resp = requests.get(NVIDIA_URL, headers=headers)
            if resp.status_code == 200:
                page = resp.content.decode('utf-8')
                if "NOTIFY ME" in page or "Сообщите мне" in page:
                    print("Not on sale")
                    time.sleep(30)
                else:
                    send_notification(domain, api, to, "Nvidia RTX 3090 is on sale", NVIDIA_URL)
                    return
            else:
                print("Invalid response code %d" % resp.status_code)
                time.sleep(300)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", dest="domain", default="")
    parser.add_argument("--api", dest="api", default="")
    parser.add_argument("--to", dest="to", default="")
    args = parser.parse_args()

    domain = args.domain
    api = args.api
    to = args.to
    needRestart = False

    if domain == "":
        domain = get_env("MAILGUN_DOMAIN", "Enter mailgun domain: ")
        needRestart = True

    if api == "":
        api = get_env("MAILGUN_API_KEY", "Enter mailgun api: ")
        needRestart = True

    if to == "":
        to = get_env("MAILGUN_TO", "Enter notification email address: ")
        needRestart = True

    if needRestart:
        cmd = [sys.executable, sys.argv[0], "--domain=" + domain, "--api=" + api, "--to=" + to]
        print("Run subprocess: %s" % cmd)
        subprocess.Popen(cmd)
    else:
        run_loop(domain, api, to)
