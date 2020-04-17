#!python
"""
* Program - Save Start Menu
* Author - [Gino Vincenzini](mailto:OpenMySourceCode@gmail.com)
* Description - This script loads the registry key in which the database for start menu 
entries are stored It then saves the binary data into incrementally counted files and 
adds an entry with a note on what changed into a text file. The note is obtained by 
showing a dialog box to the user asking for a description. The program is attached to 
a shortcut with a key combination (Ctrl+Shift+O) which allows the user to run it on the 
fly as changes are made to the start menu. Hopefully by doing this enough, the format 
of the data in the registry key can be reverse engineered so that by loading, changing, 
and then re-saving the key, and then issuing a command to refresh the start menu. Such 
would bypass Microsoft's refusal to make start menu pinning available to legitimate 
programs that wish to do it. 

* Switches: One can append the --reset switch to reset the contents of both the file and 
the directory with saved start menu entries by deleting them. 

* Notes: The code is quite quick and dirty, I intended for this to provide a useful tool 
for another project I'm working on that pins websites to the start menu from firefox. 
I don't see a likelihood for Microsoft to block this method in the future and up to date 
Windows 10 installs use this method for the startmenu storage. In fact, I'm betting they 
cannot since to do so would prevent windows itself from accessing or changing the start 
menu. Even if they changed the key name, or the file name, or worse, the format itself, 
they would only buy themselves a little time before it was determined how to work around 
it. The best course of action for Microsoft would be to provide an API to get permission 
from the user, save that permission in association with the program that requested it, 
and then allow the program access to change the start menu pins. IT managers want it, 
they want users to be able to see a set of default pins, and still be able to unpin or 
rearrange those pins as they wish. They want to be able to pin things to their users 
start menu. It seems a redesign is coming soon but the general premise is the same in
the new design. We'll have to see if they change the way this works for that redesign.
"""
## IMPORTS ##
### standard lib ###
import os
import re
import sys

### registry related ###
from lib_registry import *
from winreg import *

### gui pyside ###
import PySide2.QtCore as Core 
import PySide2.QtGui as GUI 
import PySide2.QtWidgets as Widgets

## CONSTANTS ##
USER_DIR = f"C:\\Users\\{os.getenv('username')}"

## FUNCTIONS ##
def check_for_reset():
	"""
	This function checks if the program was run using the --reset option and then
	clears out the files in the startmenus directory accordingly. Then exits
	"""
	if len(sys.argv) == 2 and sys.argv[1] == '--reset':
		for filename in os.listdir(f"C:\\Users\\{os.getenv('username')}\\startmenus\\"):
			os.remove(f"C:\\Users\\{os.getenv('username')}\\startmenus\\{filename}")
		quit()

def try_open(file_name, mode='r', buffering=-1, 
	encoding=None, errors=None, newline=None, closefd=True, opener=None):
	"""
	This function allows the user to add "try_" to the beginning of their open()
	calls so that if the file exists, it will be open for updating, if it does
	not, then it will be opened as requested.
	"""
	MODE_REGEX = '([rwax])([+]{0,1})([bt]{0,1})'
	try:
		fileHandle = open(file_name, mode, buffering, encoding, errors, 
			newline, closefd, opener)
	except FileNotFoundError:
		rw, update, bintext = re.findall(MODE_REGEX, mode)[0]
		update = '+'
		mode = f"{rw}{update}{bintext}"
		fileHandle = open(file_name, mode, buffering, encoding, errors, 
			newline, closefd, opener)
	finally:
		return fileHandle

def get_sid_from_username(username):
	"""
	This is a function recommended to the lib_registry library but which hasn't
	been included yet. It accounts for the '.DEFAULT' SID. Perhaps in the future
	I will write a more robust, OOP Registry library that makes access much more
	straightforward rather than a thin wrapper over the Windows API, The former
	would make registry access on windows a LOT more pythonic.
	"""
	keyls = get_ls_user_sids()
	for sid in keyls:
		if sid == '.DEFAULT':
			continue
		if get_username_from_sid(sid) == username:
			return sid
	raise ValueError(f"The username {username} was not found in the SID list")

def show_dialog(text, caption):
	"""
	The show dialog function is very specialized at the moment. It ONLY exists to
	get input from the user graphically (since the intention is to run this from a
	shortcut keyboard command). It then uses that input to issue a click event that
	is defined in the function itself. I'm tempted to generalize this but for now
	it will do. 
	"""
	def on_click():
		"""
		Click event handler for the dialog in "show_dialog()". It's VERY specialized
		since it writes the files from the registry key. More refactoring is needed.
		"""
		filenumber, file_name = get_next_filename()
		start_key = get_start_key()
		current_file = f"{filenumber:5}: {file_name} - {editbox.text()}"

		if start_key is not None:	
			try:
				value, _ = QueryValueEx(start_key, "Data")
				handle = try_open(f"{USER_DIR}\\startmenus\\index.txt", 'a')
				exportFile = try_open(file_name, mode="wb")
			except Exception as e:
				GUI.QMessageBox.critical(mainWidget, "An Error has Occurred",
					f"The following error has occurred: {e}")
				app.quit()
			else:
				exportFile.write(value)
				handle.write(current_file)
			finally:
				exportFile.close()
				handle.close()
				app.quit()
		else:
			raise ValueError("start_key is None")

	# Create widgets and layout objects
	app = Widgets.QApplication([])
	mainWidget = Widgets.QWidget()
	v_layout = Widgets.QVBoxLayout(mainWidget)
	label = Widgets.QLabel(caption)
	editbox = Widgets.QLineEdit()
	button = Widgets.QPushButton("Save")

	# Connect events
	Core.QObject.connect(button, Core.SIGNAL("clicked()"), on_click)
	Core.QObject.connect(editbox, Core.SIGNAL("returnPressed()"), on_click)

	# Layout the widgets
	h_layout = Widgets.QHBoxLayout()
	h_layout.addStretch()
	h_layout.addWidget(button)
	v_layout.addWidget(label)
	v_layout.addWidget(editbox)
	v_layout.addLayout(h_layout)

	# Set properties
	mainWidget.setWindowTitle(text)
	mainWidget.setLayout(v_layout)

	# Run the dialog box.
	mainWidget.show()
	return app.exec_()

def get_next_filename():
	"""
	determines the next filename in the directory, returns this tuple:
	(filenumber -> int, file_name -> str)
	"""
	filenumber = 0
	file_name = ''
	
	for startmenufile in os.listdir(f"{USER_DIR}\\startmenus\\"):
		if startmenufile.endswith('.bin'):
			numarray = re.findall('startmenu([0-9 ]{5})\\.bin', startmenufile)
			# numarray will only ever have one entry, but re.findall insists on
			# 	returning an array. To mitigate that, we enumerate it
			for i, s in enumerate(numarray):
				# int() doesn't like numbers with leading/trailing spaces,
				#	so we strip them.
				numarray[i] = s.strip()
			num = int(numarray[0])
			if num > filenumber:
				filenumber = num

	filenumber += 1
	file_name = USER_DIR + f"\\startmenus\\startmenu{filenumber:5}.bin"

	return (filenumber, file_name)

def get_start_key():
	"""
	Returns a handle of the key where start menu pins are located.
	"""
	DefaultAccount_key = OpenKey(
			HKEY_USERS,
			f"{get_sid_from_username(os.getenv('username'))}" + 
			"\\Software\\Microsoft\\Windows\\CurrentVersion\\" +
			"CloudStore\\Store\\Cache\\DefaultAccount\\")

	numKeys = get_number_of_subkeys(DefaultAccount_key)
	i = 0
	while i < numKeys:
		localKey = EnumKey(DefaultAccount_key, i)
		if localKey.endswith('$start.tilegrid$' +
			'windows.data.curatedtilecollection.tilecollection'):
			start_key = OpenKey(DefaultAccount_key, localKey)
			break
		i += 1

	if start_key is None:
		raise ValueError("Start Menu Key not found")
	else:
		start_key = OpenKey(start_key, 'Current')
		return start_key

def entry():
	"""
	Entrypoint for the program. 
	"""
	check_for_reset()
	os.system('cls' if os.name == 'nt' else 'clear')

	try:
		os.makedirs(f"C:\\Users\\{os.getenv('username')}\\startmenus\\")
	except FileExistsError:
		pass

	show_dialog("Question", "What did you change in the Start Tile Layout?")

if __name__ == "__main__": entry() # Main Function