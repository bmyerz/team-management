import github
import sys
import csv

if len(sys.argv) < 2:
    print "argument: path/to/file/containing/personal_access_token"
    print "that file should contain one line, the access token"
    print "(see your user settings | Personal access token in github enterprise)"
    exit(1)

access_token_file = sys.argv[1]
login_or_token = None

with open(access_token_file, 'r') as f:
    login_or_token = f.readlines()[0].strip()

g = github.Github(login_or_token=login_or_token, base_url='https://github.uiowa.edu/api/v3')

org = g.get_organization("cs2230-fa17")

with open('student_groups.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        team_num, student0, student1 = row
        try:
            # if repos exist already
            #r = org.get_repo("project-team-{}".format(team_num))
            #t = org.create_team("team-{}".format(team_num), repo_names=[r], permission="push")
            # if repos don't exist yet
            t = org.create_team("team-{}".format(team_num), permission="push")

            print t
        except github.GithubException as e:
            print "skip creation ", team_num
            continue

        
        # if repos don't exist yet
        r = org.create_repo("project-team-{}".format(team_num), 
            private=True, 
            team_id=t)

        user0 = g.get_user(student0)
        user1 = g.get_user(student1)
        t.add_to_members(user0)
        t.add_to_members(user1)

#for repo in g.get_user().get_repos():
#    print repo.name
    #repo.edit(has_wiki=False)
