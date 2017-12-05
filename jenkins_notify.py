#!/usr/bin/env python
# coding=utf8

import urllib.request
import base64
import time
import os


def request(url):
    request = urllib.request.Request(url)
    request.add_header('Authorization', 'Basic ' + userbase64)
    response = urllib.request.urlopen(request)
    html = response.read()
    json = eval(html)
    return json


def contains(jobs, job_name):
    for job in jobs:
        if (job['name'] == job_name):
            return True
    return False


def get_last_build(job_url):
    url = job_url + 'lastBuild/api/python'
    try:
        last_build = request(url)
        return last_build
    except (Exception) as e:
        print(url + '---' + str(e))
        return None


def load_job_list():
    api_url = jenkins_url + 'api/python'
    result_dict = request(api_url)
    remote_jobs = result_dict['jobs']
    # deal remote job delete
    for local_name in list(local_jobs.keys()):
        if not contains(remote_jobs, local_name):
            del local_jobs[local_name]

    # deal remote job add  OR  init
    for remote_job in remote_jobs:
        if not remote_job['name'] in local_jobs.keys():
            lastBuild = get_last_build(remote_job['url'])
            local_jobs[remote_job['name']] = {'name': remote_job['name'], 'url': remote_job['url'],
                                              'number': lastBuild['number'] if lastBuild is not None else 0}
    return


def fetch_newbuild(lastBuild, localJob):
    if not lastBuild['building'] and localJob['number'] < lastBuild['number']:
        localJob['number'] = lastBuild['number']
        lastBuild['name'] = localJob['name']
        return lastBuild


def fetch_newbuilds():
    builds = []
    for localJob in local_jobs:
        lastBuild = get_last_build(local_jobs.get(localJob)['url'])
        build = fetch_newbuild(lastBuild, local_jobs.get(localJob))
        if build is not None:
            builds.append(build)
    return builds


def speak_loudly(builds):
    for build in builds:
        message = fommat_message(build)
        os.system('sh /opt/tap-shell/speak.sh ' + message)
        print(message)


def fommat_message(last_build):
    message = ((last_build['description'].replace('Started by GitLab push by', '') + '你触发的构建结果为') if last_build['description'] is not None else ('手动触发构建结果为')) + \
              last_build['name'] + '构建' + ('成功' if last_build['result'] == 'SUCCESS' else '失败')
    return message


jenkins_url = 'http://172.16.144.17:8080/'
user = 'aap:6789@jkl'
userbase64 = base64.b64encode(user.encode()).decode()

local_jobs = {}

while (True):
    load_job_list()
    # print(local_jobs)

    builds = fetch_newbuilds()
    # print(builds)
    speak_loudly(builds)

    time.sleep(10)
