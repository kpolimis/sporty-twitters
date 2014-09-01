import os.path
import sys

if len(sys.argv) != 3:
    print "Wrong use of the command."
    sys.exit(1)

users_dir = sys.argv[1]
users_list = sys.argv[2]

found = []
missing = []
total = 0
with open(users_list) as ids:
    for i in ids:
        istr = i.strip()
        total += 1
        if os.path.isfile(os.path.join(users_dir, istr)):
            found.append(int(istr))
        else:
            missing.append(int(istr))

if len(missing):
    print "Missing " + str(len(missing)) + " out of " + str(total) + ": " + str(missing)
else:
    print "All users tweets have been found (total: " + str(total) + ")"
