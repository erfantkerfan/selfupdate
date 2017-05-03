#!/usr/bin/env python3

import inspect
import git
import os

__version__ = "0.1.0"
__author__ = "Broderick Carlin (beeedy)"
__email__= "broderick.carlin@gmail.com"
__license__= "MIT"


def __get_calling_file():
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
			return os.path.split(complete_path)
	raise LookupError("Module was not called by an external script.")

def __find_repo():
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
			raise LookupError("Calling script is not in a valid git repo")

		try:
			git.Repo(file_path)
			return os.path.normpath(file_path)
		except git.exc.InvalidGitRepositoryError:
			file_path = os.path.normpath(file_path + "/..")

def is_dev_env(directory, suppress_errors=False):
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
						return True
		#raise error here
		if not suppress_errors:
			raise EnvironmentError("'.devenv' found but not included in '.gitignore'.")

	return False


def test():
	repo_path = __find_repo()
	is_dev_env(repo_path)

