#!/usr/bin/env python3

import inspect
import git
import os

__version__ = "0.1.0"
__author__ = "Broderick Carlin (beeedy)"
__email__= "broderick.carlin@gmail.com"
__license__= "MIT"

global_verbosity = False


def __print(verbose, msg):
	'''
	This is a simple utility function used to help assist in 
	adding debug messages throughout the code. Print messages
	are formated as such:
	<name of calling function>:<line #> :: <msg>
	'''
	if not verbose and not global_verbosity:
		return

	stack = inspect.stack()
	calling_func = stack[1][3]
	line = stack[1][2]
	msg.replace("\n", "\n           ".format(calling_func, line))
	print("{}():{} :: {}".format(calling_func, line, msg))

def __get_calling_file(verbose=False):
	'''
	This function will go through the python call stack and find
	the script that originally called into this file. Returns a 
	tuple where the first element is a string that is the folder
	containing the calling script, and the second element is the
	name of the file name of the calling script. If a file can not
	be found for some reason a LookupError is raised to indicate
	that an external script could not be found.
	'''
	stack = inspect.stack()
	this_file = stack[0][1]
	for i in range(1, len(stack)):
		if stack[i][1] != this_file:
			complete_path = os.path.normpath(os.getcwd() + "/" + stack[i][1])
			__print(verbose, "Module was called from: {}".format(complete_path))
			return os.path.split(complete_path)

	__print(verbose, "Module was not called by an external script.")
	raise LookupError("Module was not called by an external script.")

def __find_repo(verbose=False):
	'''
	This function will go figure out if the calling python script
	is inside a git repo, and if so, return a string that is the 
	location of the base of the git repo. If the script is not, a 
	LookupError is raised to indicate it could not find the repo
	'''
	file_path, file_name = __get_calling_file()
	# walk up the file tree looking for a valid git repo, stop when we hit the base
	while True:
		if os.path.samefile(os.path.normpath(file_path), os.path.normpath("/")):
			__print(verbose, "Calling script is not in a valid git repo")
			raise LookupError("Calling script is not in a valid git repo")

		try:
			git.Repo(file_path)
			__print(verbose, "Found root of repo located at: {}".format(os.path.normpath(file_path)))
			return os.path.normpath(file_path)
		except git.exc.InvalidGitRepositoryError:
			file_path = os.path.normpath(file_path + "/..")

def __find_current_branch(repo, verbose=False):
	'''
	Simple function that returns the name of the current branch. 
	If for some reason the function fails to find the current branch
	an IOError is raised to indicate something has gone wrong. 
	'''
	assert type(repo) is git.repo.base.Repo, "Passed in repo needs to be of type 'git.repo.base.Repo'"
	branches = str(repo.git.branch()).splitlines()
	for branch in branches:
		# asterix represents current branch, search for it
		if branch[0] == "*":
			__print(verbose, "Found current branch to be: {}".format(branch[2:]))
			return branch[2:]
	__print(verbose, "Failed to find current branch")
	raise  IOError("Failed to find current branch")

def is_dev_env(directory, suppress_errors=False, verbose=False):
	'''
	This function will return 'True' if the git repo is setup to 
	be a selfupdate development environment. This indicates that 
	functions that perform destructive file manipulation will be 
	limited in scope as to not cause the script to complicate 
	development efforts when using the selfupdate library. A 
	selfupdate development environment is configured by placeing
	an empty file in the root directory of the repo simply named
	'.devenv'. This file must also be included in the .gitignore
	or a EnvironmentError will be raised. This is to avoid the 
	propogation of the development environment file to the main 
	repo and any other local repositories that would then pull 
	this file down and turn themselves into development 
	environments. This error can be suppressed by setting the 
	argument 'suppress_errors' to 'True' when calling is_dev_env().
	Suppressing this error can cause remote repos that rely on 
	selfupdate to no longer update succesfully without direct
	user input. You have been warned! 
	'''
	directory = os.path.normpath(directory)
	# see if the .devenv file even exists
	if os.path.isfile(directory + "/.devenv"):
		# it exists, so make sure a .gitignore exists and it includes .devenv
		if os.path.isfile(directory + "/.gitignore"):
			with open(directory + "/.gitignore", 'r') as gitignore:
				for line in gitignore.readlines():
					if ".devenv" in line:
						__print(verbose, "Found valid development environment")
						return True
		#raise error here
		__print(verbose, "'.devenv' found but not included in '.gitignore'.")
		if not suppress_errors:
			raise EnvironmentError("'.devenv' found but not included in '.gitignore'.")
	else:
		__print(verbose, "No '.devenv' file found in the root directory of the repo")

	return False

def pull(verbose=False):
	'''
	This function will attempt to pull any remote changes down to 
	the repository that the calling script is contained in. If 
	there are any file conflicts the pull will fail and the function
	will return. This function is *safe* and does not perform 
	destructive actions on the repo it is being called on. This 
	function returns a tuple containing 2 fields. The first is a
	boolean value that indicates if the pull was successful or not. 
	The second field contains a list of the files that were effected
	by the pull. If the pull was successful, this is the files that 
	were updated by the pull action. If the pull was unsuccesful, 
	this list contains the files that have conflicts and stopped the
	pull. All files listed in the case of a success or failure are 
	referanced relative to the base of the repository. This function 
	attempts to capture git errors but it is entirely possible that 
	it does not handle a git error correctly in which case it will be 
	raised again to be potentially handled higher up. 
	'''
	repo_path = __find_repo()
	repo = git.Repo(repo_path)

	try:
		resp = str(repo.git.pull()).splitlines()
		if resp[0] == "Already up-to-date.":
			__print(verbose, "Repository is already up to date.")
			return (True, [])

		files = [a.split("|")[0][1:-1] for a in resp[2:-1]]
		__print(verbose, "Files that were updated:" + "\n  ".join(files))
		return (True, files)

	except git.exc.GitCommandError as err:
		err_list = str(err).splitlines()

		# this is a poor and rudamentary way to tell if there was a specific error TODO: fix
		if err_list[3] == "  stderr: 'error: Your local changes to the following files would be overwritten by merge:":
			files = [a[1:] for a in err_list[4:-2]]
			__print("Pull failed. Files with conflicts:" + "\n  ".join(files))
			return (False, files)
		# we got an error we didn't expect, pass it back up
		raise

	return (True, [])

def hard_pull(check_dev=True, verbose=False):
	'''
	This function is similar in idea to the classic pull(), however
	the main differance is that this is a destructive hard pull. This
	means that any and all local changes will be discarded and the 
	local copy of all files will be made to match those pulled down 
	from the remote repo. If the calling script is in a development
	environment and return_success_for_dev is set to True, this function
	will immedietly exit so as to avoid the script removing any/all 
	progress made in a project. 
	'''
	repo_path = __find_repo()
	# this is a destructive function, to avoid problems return 'success' if in a dev environment
	if check_dev and is_dev_env(repo_path):
		__print(verbose, "Detected development environment. Aborting hard pull")
		return 

	repo = git.Repo(repo_path)
	branch = __find_current_branch(repo)

	# fetch all
	fetch_resp = str(repo.git.fetch("--all"))
	__print(verbose, "Fetched any and all changes with response: {}".format(fetch_resp))
	# reset
	reset_resp = str(repo.git.reset("--hard", "origin/{}".format(branch)))
	__print(verbose, "Completed hard pull with response: {}".format(reset_resp))
	# clean
	clean_resp = str(repo.git.clean("-f"))
	__print(verbose, "Completed clean with response: {}".format(clean_resp))

def push(verbose=False):
	'''
	'''
	
def test():
	#print(pull())
	__print(False,"BLAH BLAH")
