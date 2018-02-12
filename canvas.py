import requests
import re
import sys
import csv

if len(sys.argv) < 2:
    print "argument: path/to/file/containing/access_token"
    print "that file should contain one line, the access token"
    print "(see your user settings in Canvas)"
    exit(1)

access_token_file = sys.argv[1]
access_token = None

with open(access_token_file, 'r') as f:
    access_token = f.readlines()[0].strip()

api_url = 'https://uiowa.instructure.com/api/v1/'

session = requests.Session()
session.headers = {'Authorization': 'Bearer %s' % access_token}

no_pagination = '?per_page=200'

# CS2230 Fall 2017 canvas course id
course_id = 64804

with open('student_groups.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')

    r = session.get(api_url+'courses/{0}/groups{1}'.format(course_id, no_pagination))
    groups = r.json()
    for group in groups:
        match_name = re.match(r'Project pair (\d+)', group['name'])
        if match_name is not None:
            r = session.get(api_url+'groups/{0}/users'.format(group['id']))
            r = r.json()
            if len(r) == 2:
                writer.writerow([match_name.group(1), r[0]['sis_login_id'], r[1]['sis_login_id']])
            # else:  print "{0} has wrong number of users".format(group['name'])
