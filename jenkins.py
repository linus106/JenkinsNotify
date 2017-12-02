import urllib.request
import base64
import time



def request ( url ) :
    request = urllib.request.Request(url)
    request.add_header('Authorization', 'Basic ' + userbase64)
    response = urllib.request.urlopen(request)
    html = response.read()
    json = eval(html)
    return json

def contains (jobs , jobName) :
    for job in jobs :
        if(job['name'] == jobName) :
            return True
    return False


def getLastBuild (jobUrl) :
    url = jobUrl + 'lastBuild/api/python'
    try:
        lastBuild = request(url)
        return lastBuild
    except (Exception) as e:
        print(url + '---' + str(e))
        return None

def loadJobList () :
    apiUrl = jenkinsUrl + 'api/python'
    resultDict = request(apiUrl)
    remoteJobs = resultDict['jobs']
    # 处理远端删除的job
    for localName in list(localJobs.keys()) :
        if not contains(remoteJobs, localName) :
            del localJobs[localName]

    # 处理远端新增  or 首次加载的job
    for remoteJob in remoteJobs :
        if not remoteJob['name'] in localJobs.keys() :
            lastBuild = getLastBuild(remoteJob['url'])
            localJobs[remoteJob['name']] = {'name' : remoteJob['name'], 'url' : remoteJob['url'], 'number' : lastBuild['number'] if lastBuild is not None else 0 }
    return

def fetchNewBuild (lastBuild, localJob) :
    if not lastBuild['building'] and localJob['number'] < lastBuild['number'] :
        localJob['number'] = lastBuild['number']
        return lastBuild

def fetchNewBuilds () :
    builds = []
    for localJob in localJobs :
        lastBuild = getLastBuild(localJobs.get(localJob)['url'])
        build = fetchNewBuild(lastBuild, localJobs.get(localJob))
        if build is not None :
           builds.append(build)
    return builds

def speakLoudly (builds) :
    for build in builds :
        print(fommatMessage(build))

def fommatMessage ( lastBuild ) :
    message = lastBuild['fullDisplayName'] + '构建' + ('成功' if lastBuild['result'] == 'SUCCESS' else '失败') + (lastBuild['description'] if lastBuild['description'] is not None else '')
    return message


jenkinsUrl = 'http://172.16.144.17:8080/'
testUrl = "http://172.16.144.17:8080/job/TAP_LICENSE_CENTER_DOCKER/lastBuild/api/python"
user = 'aap:6789@jkl'
userbase64 = base64.b64encode(user.encode()).decode()


localJobs = {}

while (True) :
    loadJobList()
    print(localJobs)

    builds = fetchNewBuilds()
    print(builds)
    speakLoudly(builds)
    time.sleep(10)
