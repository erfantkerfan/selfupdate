selfupdate 
=============== 
:Authors: Broderick Carlin
:Version: V0.1.0

Python library that allow scripts to easily update themselves if they are in a git repo. The idea is to allow a simple short command with minimal to no arguments update a script that is contained with a git repo by pulling any changes from the remote repo. 

A basic use case: 
  An embedded linux platform does not have a static IP yet is guarenteed to always be conntected to the internet. Rather than setting up infustructure to make sure the scripts running on the devices are automatically updated to the most recent version you can have the scripts check and update themselves. This is the basic idea behind selfupdate, allowing repo's to be quickly cloned and run on any system without having to worry about how they will be kept up to date with changes in the remote repo

This initial version is very light on features however should contain core functionality. No guarentees are made about the reliability of this module. Please keep in mind this is still in alpha!

How to install
==========

This can be easily installed by using pip and running:

```pip install selfupdate```

How to use
==========

Example:

>>> from selfupdate import update
    update()

and when this script is run, assuming it is contained within a git repo, it will merge the newest changes from the remote repo while also pushing up any local changes.

If you would like more control over the update processes please see these available parameters:

- **force** : boolean, default: *False*

  In the case where there are conflicts in the pull or push of the update, setting force to *True* will cause selfupdate to force the pull and push to take place. Note that this is a destructive action and can cause loss of work and information. This should be left as the default unless your specific application produces a lot of conflicts and you can predict the conflicts.  
- **check_dev** : boolean, default: *True*

  With the features that exist already, it is possible to write a script that will not allow you to test any possible changes without the script forcefully reverting any and all changes. This sounds like an absolutely development nightmare and so by having **check_dev** set to *True* the module can detect if you are within a development environment and disable all destructive actions on your local machine. Please see below for what a development environment is and how to set one up before your scripts start to revert their own changes. 
- **message** : string, default: "Pushing up changes with python selfupdate"

  Whenever a commit is made this is the commit message. Simple enough.
- **username** : string, default: None

  It is highly likely that your remote repo is password protected if you cloned using https rather than SSH. If this is the case you can use this paramter to pass in a username to be used to access the remote repo. PLEASE do not hard code in your credentials for security reasons. You don't want a script that has the ability to commit itself to also have your credentials in plain text.
- **password** : string, default: None

  Goes along with the username. See above. 
- **verbose** : boolean, default: False

  There is a lot going on behind the scenes. If you are curious what is all going on or you want to debug some weird behavior it can be helpful to enable this.
  
Development Environment
=======================

This really is not anything too fancy, but it can help to ease the headache of trying to develop and debug a script that has the ability to revert any changes made to it. A *development environment* is just a single file that notifies the update module that it should under no circumstances perform destructive actions on the repo. There are two simple steps needed to setup what selfupdate considers a *development environment*

1. Create an empty file in the foot folder of the repo (same level as your ``.gitignore``, ``.git``, etc.) titled ``.devenv``

2. By including this file in your repo it could be possible that it get pushed up to the remote repo and subsequently pulled down by scripts using selfupdate. This could lead to a situation where a script would no longer be self updating and need direct interaction. Luckly, the selfupdate module attempts to reduce this risk as much as possible by throwing an error if a ``.devenv`` file exists but it is not included in the ``.gitignore``. So the 2nd and final step to setup a development environment is just to add ``.devenv`` to the ``.gitignore``
  
  
