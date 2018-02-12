import csv
import re
import pandas
import random

# currently accounts for apostrophe in last name, dual names
firstlast_pat = re.compile(r"[A-Za-z]+ [A-Za-z']+( [A-Za-z']+)?")


def is_valid_response(s):
    return (firstlast_pat.match(s) or s == "") \
        and s not in {"No Preference"}


def get_users(user_file):
    with open(user_file, 'rb') as csvfile:
        inp = csv.reader(csvfile, delimiter=',')
        burn = 3
        i = 0
        students = []
        for row in inp:
            name = row[0]
            if i >= burn and name != "Test Student":
                students.append(name)

            i += 1

        return students


def get_preferences(preference_results):
    with open(preference_results, 'rb') as csvfile:
        inp = csv.reader(csvfile, delimiter=',')
        burn = 1
        i = 0
        students = []
        for row in inp:
            name, want, dontwant = row[0], row[9], row[11]
            if i >= burn:
                # cleanup: remove invalid responses
                if not is_valid_response(want):
                    print "response [{}] thrown out".format(want)
                    want = ""
                if not is_valid_response(dontwant):
                    print "response [{}] thrown out".format(dontwant)
                    dontwant = ""

                students.append((name, want, dontwant))

            i += 1

        return students


def get_preferences_for_all(students, preferences):
    students_df = pandas.DataFrame(data={"name": students})
    preferences_df = pandas.DataFrame(data={"name": [x[0] for x in preferences],
                                            "want": [x[1] for x in preferences],
                                            "dontwant": [x[2] for x in preferences]})

    # left outer join
    df = students_df.merge(preferences_df, how='left', left_on=["name"], right_on=["name"])  #TODO: use 'validate' argument in different version of pandas
    df = df.fillna("")
    return df


def get_previous_groups(groups):
    with open(groups, 'rb') as csvfile:
        inp = csv.reader(csvfile, delimiter=',')
        burn = 0
        i = 0
        groups = {}
        for row in inp:
           for i in range(1, 5):
               for j in range(1, 5):
                   if i != j and row[i] != "" and row[j] != "":
                       if row[i] not in groups:
                           groups[row[i]] = set()
                       groups[row[i]].add(row[j])


        # TODO: cleanup this: student wasn't in a group for some reason
        groups["OMITTED"] = set()

        return groups


class Group(object):
    def __init__(self, students):
        self.students = tuple(students)

    def score(self, preferences, groups):
        wantWeight = 1.0
        dontwantWeight = -10.0**10
        previousGroupWeight = -0.5 / 2   # half to avoid double counting

        sc = 0.0
        for nx in self.students:
            for ny in self.students:
                # print nx, ny, groups[nx], groups[ny]
                nxrow = preferences[preferences["name"] == nx]
                if nxrow["want"].iloc[0] == ny:
                    sc += wantWeight
                if nxrow["dontwant"].iloc[0] == ny:
                    sc += dontwantWeight
                if nx in groups[ny]:  # don't check other way around to not overcount
                    sc += previousGroupWeight

        return sc

    def __str__(self):
        return "Group {}".format(str(self.students))

    def __repr__(self):
        return "Group {}".format(str(self.students))

    def __hash__(self):
        return hash(self.students)


def create_initial_groups(students, n):
    groups = []
    groups.append([])
    i = 0
    for row in students.itertuples():
        if len(groups[i]) == 4:
            i += 1
            groups.append([])
        groups[i].append(row.name)

    return tuple([Group(g) for g in groups])

# TODO: heuristic start with wants
    print "Created {0} wanted {1}".format(len(groups), n)
    return groups


class MutableInteger(object):
    def __init__(self, i):
        self.i = i

    def get(self):
        return self.i

    def set(self, i):
        self.i = i


# currently a strictly hill-climbing algorithm
def optimize(initial, allprefs, prev_groups):
    seen = set()
    maxseen = MutableInteger(-10**10)

    def search(assignment):
        if assignment in seen:
            return
        else:
            seen.add(assignment)

        score = sum([x.score(allprefs, prev_groups) for x in assignment])
        if score > maxseen.get():
            print "New score {0} for {1}".format(score, assignment)
            maxseen.set(score)

            for trial in range(0, len(allprefs)**2):  # arbitrarily stop branching when done with N^2 swaps
                fromi = random.randint(0, 14)
                toi = random.randint(0, 14)
                fromp = random.randint(0, 2) # or 3?
                top = random.randint(0, 2)   # or 3? leave last student in place
                newstudents = [list(g.students) for g in assignment]
                f = newstudents[fromi][fromp]
                t = newstudents[toi][top]
                #print "swap ", f, "with", t
                newstudents[fromi][fromp] = t
                newstudents[toi][top] = f
                newasi = tuple([Group(g) for g in newstudents])

                search(newasi)
        else:
            #print "failed with score ", score
            pass

    search(initial)


# do it

dir = "."

users = get_users("{}/2018-02-11T1458_Grades-CS-2630-0001_Spr18.csv".format(dir))
prefs = get_preferences("{}/Forming New Teams Survey Student Analysis Report.csv".format(dir))
prev_groups = get_previous_groups("{}/student_groups_wk1.csv".format(dir))

allprefs = get_preferences_for_all(users, prefs)


# initialize a group assignment
initial = create_initial_groups(allprefs, 15)

# run optimization
optimize(initial, allprefs, prev_groups)
