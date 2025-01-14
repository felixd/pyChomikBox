import argparse

from ChomikBox.ChomikBox import Chomik, ChomikFolder, ChomikFile

# This code lists all free downloadable files from Chomik and saves this list to file

paths = ['/test/','/test2/']
out_f = r'test-chomikList.txt'

p = argparse.ArgumentParser()
p.add_argument('login', help="Chomikuj login/email")
p.add_argument('password', help="Chomikuj password")
args = p.parse_args()

c = Chomik(args.login, args.password)
c.login()

folders = [c.get_path(path) for path in paths]
files = []

while folders:
    for f in folders:
        if isinstance(f, ChomikFile):
            files.append(f)
        elif isinstance(f, ChomikFolder):
            folders.extend(f.folders_list())
            files.extend(f.files_list(only_downloadable=True))
        folders.remove(f)

with open(out_f, 'w+') as out:
    for f in files:
        print(f.name, file=out)
        print(f.path, file=out)

c.logout()
