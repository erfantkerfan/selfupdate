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
	while True:
		if os.path.samefile(os.path.normpath(file_path), os.path.normpath("/")):
			raise LookupError("Calling script is not in a valid git repo")

		try:
			git.Repo(file_path)
			return file_path
		except git.exc.InvalidGitRepositoryError:
			file_path = os.path.normpath(file_path + "/..")



def test():
	print(__find_repo())
