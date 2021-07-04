
interfan.pyw:	mainWindow.py
	chmod 755 interfan.pyw


mainWindow.py:	mainWindow.ui
	pyuic5 mainWindow.ui -o mainWindow.py
