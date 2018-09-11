import argparse
import os
import subprocess as sp

def arg_parser():

    parser = argparse.ArgumentParser(description = 'ide jon valami')
    parser.add_argument('--data',       required = True, help = 'data csv file')
    parser.add_argument('--user-name',  required = True, help = 'github user name')
    parser.add_argument('--password',   required = True, help = 'github password')
    param_dict = {}
    args  = parser.parse_args()
    param_dict["data"] = args.data
    param_dict["user-name"] = args.user_name
    param_dict["password"] = args.password
    return param_dict


def data_csv_reader(param_dict):
    F = open(param_dict["data"], "r")
    lines = F.readlines()

    for x in range(1, len(lines)):
        line = lines[x].split("\n")[0]

        if line.startswith("#"):
            # Ignore lines that start with #
            pass
        else:
            attr = get_bug_attribute(line)
            git_cmd(attr, param_dict["user-name"], param_dict["password"])

    F.close()


def get_bug_attribute(line):
    attr = {}
    attr["bugID"] = line.split(";")[0]
    attr["repo"] = line.split(";")[1]
    attr["co_folder"] = line.split(";")[2]
    attr["hash"] = line.split(";")[3]
    attr["include"] = line.split(";")[4]
    attr["orig_patch_folder"] = line.split(";")[5]
    attr["clean_patch_folder"] = line.split(";")[6]
    return attr

def git_cmd(attr, user_name, password):
    git_clone(attr)
    git_apply(attr, user_name, password)


def git_clone(attr):
    if os.path.isdir(attr["co_folder"]):
        rm_cmd = "rm -R "+str(attr["co_folder"])
        sp.call(rm_cmd, shell=True)

    os.makedirs(attr["co_folder"])

    os.chdir(attr["co_folder"])
    clone_cmd = "git clone "+str(attr["repo"])
    sp.call(clone_cmd, shell=True)
    os.chdir( os.listdir( "./" )[0] )

    checkout_cmd = "git checkout "+str(attr["hash"])+"^"
    sp.call(checkout_cmd, shell=True)

    git_tag_cmd = "git tag Bug-"+str(attr["bugID"])
    sp.call(git_tag_cmd, shell=True)


def git_apply(attr, user_name, password):
    git_apply_cmd = "git apply --include="+str(attr["include"])+" "+str(attr["clean_patch_folder"])+"/"+str(attr["hash"])+".patch"
    sp.call(git_apply_cmd, shell=True)
    sp.call("git add --all", shell=True)
    git_commit_cmd = "git commit -m \"Bug-"+str(attr["bugID"])+" test\""
    sp.call(git_commit_cmd, shell=True)
    git_tag_cmd = "git tag Bug-"+str(attr["bugID"])+"-test"
    sp.call(git_tag_cmd, shell=True)


    checkout_cmd = "git checkout HEAD^"
    sp.call(checkout_cmd, shell=True)
    git_apply_cmd = "git apply --exclude="+str(attr["include"])+" "+str(attr["clean_patch_folder"])+"/"+str(attr["hash"])+".patch"
    sp.call(git_apply_cmd, shell=True)
    sp.call("git add --all", shell=True)
    git_commit_cmd = "git commit -m \"Bug-"+str(attr["bugID"])+" fix\""
    sp.call(git_commit_cmd, shell=True)
    git_tag_cmd = "git tag Bug-"+str(attr["bugID"])+"-fix"
    sp.call(git_tag_cmd, shell=True)


    checkout_cmd = "git checkout HEAD^"
    sp.call(checkout_cmd, shell=True)
    git_apply_cmd = "git apply "+str(attr["clean_patch_folder"])+"/"+str(attr["hash"])+".patch"
    sp.call(git_apply_cmd, shell=True)
    sp.call("git add --all", shell=True)
    git_commit_cmd = "git commit -m \"Bug-"+str(attr["bugID"])+" full\""
    sp.call(git_commit_cmd, shell=True)
    git_tag_cmd = "git tag Bug-"+str(attr["bugID"])+"-full"
    sp.call(git_tag_cmd, shell=True)

    """checkout_cmd = "git checkout HEAD^"
    sp.call(checkout_cmd, shell=True)
    git_apply_cmd = "git apply "+str(attr["orig_patch_folder"])+"/"+str(attr["hash"])+".patch"
    sp.call(git_apply_cmd, shell=True)
    git_commit_cmd = "git commit -a -m \"Bug-"+str(attr["bugID"])+" orig\""
    sp.call(git_commit_cmd, shell=True)
    git_tag_cmd = "git tag Bug-"+str(attr["bugID"])+"-orig"
    sp.call(git_tag_cmd, shell=True)"""

    checkout_cmd = "git checkout "+str(attr["hash"])
    sp.call(checkout_cmd, shell=True)
    git_tag_cmd = "git tag Bug-"+str(attr["bugID"])+"-orig"
    sp.call(git_tag_cmd, shell=True)

    push_attr = str(attr["repo"]).replace("https://", "https://"+str(user_name)+":"+str(password)+"@")

    git_push_tag_cmd = "git push "+str(push_attr)+" --tags"
    sp.call(git_push_tag_cmd, shell=True)


param_dict = arg_parser()
data_csv_reader(param_dict)
