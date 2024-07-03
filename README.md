# Automatic-File-Transfer
> This program does multiple file transfers from different folders to different folders simultaneously.

## Table of Contents
* [Requirements](#-requirements)
* [Installation](#-installation)
* [Usage](#-usage)
* [To Do](#-to-do)

## 💻 Requirements
- Python 3.x or newer

## 🚀 Installation
Clone this repository and cd into source repository:
```
git clone https://github.com/danillo-de-paula-ss/Automatic-File-Transfer.git
cd Automatic-File-Transfer
```

Then install the dependencies:
```
pip install -r requirements.txt
```

Note: Windows users can download an .exe file in [Releases](https://github.com/danillo-de-paula-ss/Automatic-File-Transfer/releases) and place it in any location on their [PATH](https://en.wikipedia.org/wiki/PATH_%28variable%29) except for %SYSTEMROOT%\System32 (e.g. do not put in C:\Windows\System32). The .exe program file doesn't need Python installed.

## ☕ Usage
Inside the source repository, run the file `auto_file_transfer.py` with this command:
```
python auto_file_transfer.py
```

When you run it, the program will display 5 options in the console that you can choose from. Among the options are:
- [Create Task](#create-task)
- [Edit Task](#edit-task)
- [Delete Task](#delete-task)
- [Start Program](#start-program)
- [Exit Program](#exit-program)

### Create Task
Allows you to create a task for the program. You can give the task a name, choose the source directory, choose the destination directory, choose the types of files that the program will transfer and choose which files the program should ignore.

### Edit Task
Allows you to edit any existing task. If you leave any field blank, the data in that field does not change.

### Delete Task
Allows you to delete a task.

### Start Program
Starts file transfers according to selected tasks. Type "all" to run all tasks.

### Exit Program
Exit the program.

## 📋 To Do
* Create a graphical user interface (GUI)
