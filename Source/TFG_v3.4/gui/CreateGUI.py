import os, sys
import cv2
import Tkinter as tk
import tkFileDialog, tkMessageBox
from PIL import ImageTk, Image
import PIL

from gui import ScoreGUI

THRESHOLD = 50

##   Creates the graphic interface by means of windows
#
#	@author Monica Villanueva Aylagas
#	@date 07/02/2015
class CreateGUI():
	
	root = None
	scorePath = None
	savePath = None
	patterns = []
	spinValues = [None, None, None]


	##  __init__(self): Constructor. Create the initial window and attach callback 
	#   methods to menu options.
	def __init__(self):

		self.root = tk.Tk()
		self.root.title("MScrivener")
		
		# define options for opening or saving a file
		self.root.file_opt = options = {}
		options['defaultextension'] = '.jpg .png .bmp'
		options['filetypes'] = [('image files', '.jpg .png .bmp'), ('all files', '.*')]
		options['initialdir'] = 'C:\\'
		options['parent'] = self.root
		options['title'] = 'Select your score'
	
		# defining options for opening a directory    
		self.root.save_opt = options = {}
		options['defaultextension'] = '.jpg .png .bmp'
		options['filetypes'] = [('image files', '.jpg .png .bmp'), ('all files', '.*')]
		options['initialdir'] = 'C:\\'
		options['initialfile'] = 'OMR.xml'
		options['parent'] = self.root
		options['title'] = 'Save your XML'
		
		global widgetList
		widgetList = []  
		
		#Menu
		menu = tk.Menu(self.root)
		self.root.config(menu=menu)
		
		filemenu = tk.Menu(menu)
		menu.add_cascade(label="File", menu=filemenu) 
		filemenu.add_command(label="Open...", command=self.askopenfilename)
		filemenu.add_command(label="Save As...", command=self.asksaveasfilename)
		filemenu.add_separator()
		filemenu.add_command(label="Exit", command=self.root.quit)
		
		toolsmenu = tk.Menu(menu)
		menu.add_cascade(label="Tools", menu=toolsmenu) 
		toolsmenu.add_command(label="Start recognition", command=self.run)
		
		helpmenu = tk.Menu(menu)
		menu.add_cascade(label="Help", menu=helpmenu)
		helpmenu.add_command(label="About...", command=self.help)
		
		#Info text    
		info = "By default, the generated XML will be saved in the same folder as the input score.\nIf you want to change the directory, click 'Save'\n"
		label = tk.Label(self.root, text=info)
		label.pack()
		widgetList.append(label)
		
		#Logo image
		datadir = "data/gKey.jpeg"
		if not hasattr(sys, "frozen"):  #not packed
			datadir = 'gKey.jpeg'
		elif "_MEIPASS2" in os.environ: #one.file temp's directory
			datadir = os.path.join(os.environ["_MEIPASS2"], datadir)
		else:   #one-dir
			datadir = os.path.join(os.path.dirname(sys.argv[0]), datadir)
		cvimg = cv2.imread(datadir, 0)     
		img = PIL.Image.fromarray(cvimg)
		imgtk = PIL.ImageTk.PhotoImage(image=img) 
		labelimg = tk.Label(self.root, image=imgtk, anchor=tk.CENTER)
		labelimg.pack()  
		widgetList.append(labelimg)    
		
		#Create frame, scrolls and canvas
		self.frame = tk.Frame(self.root, relief=tk.SUNKEN)
		self.frame.grid_rowconfigure(0, weight=1)
		self.frame.grid_columnconfigure(0, weight=1)
			 
		#Canvas
		self.canvas = tk.Canvas(self.frame)  
		self.canvas.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
		# set first image on canvas
		self.item = self.canvas.create_image(0, 0)
		self.canvas.configure(scrollregion=self.canvas.bbox('all'))
		
		self.frame.pack(fill=tk.BOTH, expand=tk.YES)
		
		#Status bar
		self.status = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
		self.status.pack(side=tk.BOTTOM, fill=tk.X)
		
		
		self.root.mainloop()
		
		
		
	"""CALLBACK METHODS"""  
	##  help(self): prompts a window urging to read the manual 
	def help(self):    
		tkMessageBox.showinfo(
			"Help",
			"For further help, read the manual. You can find it in the compressed archive."
		)
		
	
	##  askopenfilename(self): save the path to open and calls changeImgCanvas
	#   to show the score (img)
	def askopenfilename(self):    
		# get filename
		self.scorePath = tkFileDialog.askopenfilename(**self.root.file_opt)
		self.changeImgCanvas()
	   
	##  asksaveasfilename(self): save the path in which you want to save the resultant XML.
	#   If this method is not called, by default the XML will be saved
	#   in the same directory as the original image, with the same name.
	def asksaveasfilename(self):    
		# get filename
		self.savePath = tkFileDialog.asksaveasfilename(**self.root.save_opt)
		

	##  click(self): save the coordinates you clicked on. 
	#   @param event: click event that contains the coordinates
	def click(self, event): 
		global ix,iy  
		
		pos = self.calcPosition(event.x, event.y)
		ix,iy = pos[0], pos[1] #event.x,event.y


	##  unclick(self): saves the coordinates where you released the mouse button.
	#   With the saved coordinates, obtains the pattern
	#
	#   @param event: click event that contains the coordinates
	def unclick(self, event):  
		pos = self.calcPosition(event.x, event.y)
		
		#error management
		if ix == None:
			return

		#adjust area to pattern
		self.possiblePat = self.adjustArea(pos)
		
		self.next()
			
		#remove callback
		self.canvas.unbind('<Button-1>')
		self.canvas.unbind('<ButtonRelease-1>')
		
		#show wizard again and focus
		self.wizard.deiconify()
		self.wizard.focus_set()  
	
	
	
	##  run(self): creates a wizard that guides you through choosing signatures and patterns.
	def run(self):
		#Reset values
		self.status.configure(text='')
		self.patterns = []
		self.recog = False
		
		#Error management
		if self.scorePath == "" or self.scorePath == None:
			tkMessageBox.showerror ('Error', 'You have not chosen a score yet')
			return
		
		#By default, XML path = score path
		path = self.scorePath.split('.', 1)
		self.savePath = path[len(path) - 2]
		self.savePath += '.xml'
				  
		#Create wizard
		self.wizard = tk.Toplevel(self.root)
		self.wizard.title('Wizard')
		self.wizard.geometry('500x250')
		self.wizard.lift(self.root)
		self.wizard.resizable(0,0)
		
		x = (self.root.winfo_screenwidth() / 2) - (500 / 2)  
		y = (self.root.winfo_screenheight() / 2) - (250 / 2)
		self.wizard.geometry('+%d+%d' % (x, y))
		
		time = tk.Frame(self.wizard)
		self.firstWizard = tk.Label(time, text='\nInsert the time signature\n').pack()
		self.num = tk.Spinbox(time, from_=1, to=63, width=4, state = 'readonly')
		self.num.pack()
		self.den = tk.Spinbox(time, values=(1, 2, 4, 8, 16, 32), width=4, state = 'readonly')
		self.den.pack()
		time.pack(side=tk.TOP)
		
		self.key = tk.Frame(self.wizard)
		tk.Label(self.key, text='\nInsert the key signature\n').pack()
		#tk.Label(self.key, text=' ').pack()
		tk.Label(self.key, text='Example: \n1 = G/e\n-1 = F/d').pack()
		tk.Label(self.key, text=' ').pack()
		#default value
		var = tk.StringVar(self.root)
		var.set("0")
		self.keyBox = tk.Spinbox(self.key, from_=-7, to=7, width=4, state = 'readonly', textvariable=var) 
		self.keyBox.pack()               
		
		whole = tk.Frame(self.wizard)
		tk.Label(whole, text='\nAre there whole notes? If so, click on one.').pack()    
		tk.Label(whole, text='\nThe program will adjust the pattern\nto lookl like this:').pack()
		#example
		datadir = "data/exampleWhole.png"
		if not hasattr(sys, "frozen"):  #not packed
			datadir = 'exampleWhole.png'
		elif "_MEIPASS2" in os.environ: #one.file temp's directory
			datadir = os.path.join(os.environ["_MEIPASS2"], datadir)
		else:   #one-dir
			datadir = os.path.join(os.path.dirname(sys.argv[0]), datadir)
		cvimg = cv2.imread(datadir, 0)     
		img = PIL.Image.fromarray(cvimg)
		self.wholeimg = PIL.ImageTk.PhotoImage(image=img)        
		tk.Label(whole, image=self.wholeimg).pack()      
		
		half = tk.Frame(self.wizard)
		tk.Label(half, text="\nAre there half notes? If so, click on it's head.").pack()
		tk.Label(half, text='\nThe program will adjust the pattern\nto look like this:').pack()
		#example
		datadir = "data/exampleHalf.jpg"
		if not hasattr(sys, "frozen"):  #not packed
			datadir = 'exampleHalf.jpg'
		elif "_MEIPASS2" in os.environ: #one.file temp's directory
			datadir = os.path.join(os.environ["_MEIPASS2"], datadir)
		else:   #one-dir
			datadir = os.path.join(os.path.dirname(sys.argv[0]), datadir)
		cvimg = cv2.imread(datadir, 0)     
		img = PIL.Image.fromarray(cvimg)
		self.halfimg = PIL.ImageTk.PhotoImage(image=img)        
		tk.Label(half, image=self.halfimg).pack()
		
		black = tk.Frame(self.wizard)
		tk.Label(black, text="\nAre there quarter notes or notes with\nshorter duration? If so, click on it's head.").pack()
		tk.Label(black, text="\nThe program will adjust the pattern\nto look like this:").pack()
		#example
		datadir = "data/exampleBlack.jpg"
		if not hasattr(sys, "frozen"):  #not packed
			datadir = 'exampleBlack.jpg'
		elif "_MEIPASS2" in os.environ: #one.file temp's directory
			datadir = os.path.join(os.environ["_MEIPASS2"], datadir)
		else:   #one-dir
			datadir = os.path.join(os.path.dirname(sys.argv[0]), datadir)
		cvimg = cv2.imread(datadir, 0)     
		img = PIL.Image.fromarray(cvimg)
		self.blackimg = PIL.ImageTk.PhotoImage(image=img)        
		tk.Label(black, image=self.blackimg).pack()
		
		correctPat_whole = tk.Frame(self.wizard)
		tk.Label(correctPat_whole, text="\nIs this the pattern you wanted?").pack()
		#example
		datadir = "data/exampleBlack.jpg"
		if not hasattr(sys, "frozen"):  #not packed
			datadir = 'exampleBlack.jpg'
		elif "_MEIPASS2" in os.environ: #one.file temp's directory
			datadir = os.path.join(os.environ["_MEIPASS2"], datadir)
		else:   #one-dir
			datadir = os.path.join(os.path.dirname(sys.argv[0]), datadir)
		cvimg = cv2.imread(datadir, 0)     
		img = PIL.Image.fromarray(cvimg)
		self.patImg = PIL.ImageTk.PhotoImage(image=img)        
		self.correct = tk.Label(correctPat_whole, image=self.patImg)
		self.correct.pack()        
		
		correctPat_half = tk.Frame(self.wizard)
		tk.Label(correctPat_half, text="\nIs this the pattern you wanted?").pack()
		
		correctPat_black = tk.Frame(self.wizard)
		tk.Label(correctPat_black, text="\nIs this the pattern you wanted?").pack()
		tk.Label(correctPat_black, text="Click 'Finish' to start the recognition").pack()
		
		
		self.pages = [time, self.key, whole, correctPat_whole, half, correctPat_half, black, correctPat_black]
		self.current = time
		
		self.nextButton = tk.Button(self.wizard, text='Next', command=self.saveTimeSig)
		self.nextButton.pack(side=tk.RIGHT, padx=20, pady=20, anchor=tk.S)
		self.prevButton = tk.Button(self.wizard, text='Previous', command=self.prev)
		self.prevButton.pack(side=tk.LEFT, padx=20, pady=20, anchor=tk.S)

	
	
	##  next(self): Moves the wizard to the next page
	def next(self):
		self.move(+1)
		
	##  next2(self): Moves the wizard to the page after the next one
	def next2(self):
		self.move(+2)
	
	##  prev(self): Moves the wizard to the previous page
	def prev(self):
		self.move(-1)
		
	##  move(self, dir): Actually moves the wizard and updates its content.
	#   @param dir: Number of pages to move
	def move(self, dir):
		idx = self.pages.index(self.current) + dir
		
		#first page
		if idx < 0:
			return   
		
		if idx == 0:                 
			self.nextButton = tk.Button(self.wizard, text='Next', command=self.saveTimeSig)
			self.prevButton.config(text='Previous', command=self.prev)
			
		elif idx == 1:
			
			tk.Label(self.key, text="\nThe stave recognition will start now.\nIt could take a few moments").pack()
			self.status.configure(text="Recognizing...")
			
			self.nextButton.config(text='Next', command=self.saveKeySig)
			self.prevButton.config(text='Previous', command=self.prev)
			
		elif idx == 2 or idx == 4 or idx == 6:
			if self.recog == False:
				#Start stave recognition
				self.scoreG = ScoreGUI.ScoreGUI(self.root, self.cvimg)
				self.recog = True
				
			self.nextButton.config(text='Yes', command=self.choosePattern)
			if idx == 6:
				self.prevButton.config(text='Finish', command=self.noBlack) 
			else:
				self.prevButton.config(text='No', command=self.nextPattern)
			
		elif idx == 3 or idx == 5:
			self.nextButton.config(text='Yes', command=self.savePattern)
			self.prevButton.config(text='No', command=self.reChoosePattern)           
			
			#check if there is a correct packed
			ls = self.pages[idx].winfo_children()
			cont = 0
			for it in ls:
				if it.widgetName == 'label':
					cont += 1   
			if cont > 1:
				self.correct.forget()  
				
			#change pattern
			img = PIL.Image.fromarray(self.possiblePat)      
			self.patImg = PIL.ImageTk.PhotoImage(image=img)
			self.correct = tk.Label(self.pages[idx], image=self.patImg)                   
			self.correct.pack()
			
		elif idx == 7:
			self.nextButton.config(text='Finish', command=self.savePattern)
			self.prevButton.config(text='No', command=self.reChoosePattern)

			#check if there is a correct packed
			ls = self.pages[idx].winfo_children()
			cont = 0
			for it in ls:
				if it.widgetName == 'label':
					cont += 1   
			if cont > 1:
				self.correct.forget() 
				
			#change pattern
			img = PIL.Image.fromarray(self.possiblePat)   
			self.patImg = PIL.ImageTk.PhotoImage(image=img)
			self.correct = tk.Label(self.pages[idx], image=self.patImg)
			self.correct.pack()
			
			
		self.current.pack_forget()
		self.current = self.pages[idx]
		self.current.pack(side=tk.TOP)

	##  saveTimeSig(self): Saves the values of the time signature 
	#   (spin box) into a list
	def saveTimeSig(self):
		self.spinValues[0] = self.num.get()
		self.spinValues[1] = self.den.get()
		self.next()
		
	##  saveKeySig(self): Saves the value of the key signature 
	#   (spin box) into a list
	def saveKeySig(self):
		self.spinValues[2] = self.keyBox.get()
		self.next()
		
	##  nextPattern(self): Saves a null value as a patter and 
	#   skips certain wizard pages.    
	def nextPattern(self):
		self.move(+2)
		self.patterns.append(None)
	
	##  noBlack(self): Saves a null value as a black pattern to
	#   start the recognition process.    
	def noBlack(self):
		self.possiblePat(None)
		self.savePattern()
	
	##  savePattern(self): Saves the current pattern into the list and
	#   unbind the mouse event callback methods   
	def savePattern(self):
		self.patterns.append(self.possiblePat)
		if len(self.patterns) < 3:
			self.move(+1)
		else:
			#remove callback
			self.canvas.unbind('<Button-1>')
			self.canvas.unbind('<ButtonRelease-1>')
			
			#kill wizard and focus root   
			self.root.focus_set()  
			self.wizard.destroy() 
			self.root.update()
			
			#start recognition
			self.scoreG.start(self.spinValues, self.patterns, self.savePath)        
	

	##	reChoosePattern(self): Call choosePattern and reset the wizard page
	def reChoosePattern(self):
		self.choosePattern()
		self.prev()

	##	choosePattern(self): Allow the user to choose a pattern biding the
	#	mouse event callback methods  
	def choosePattern(self):        
		#hide wizard and focus root
		self.root.focus_set()
		self.wizard.withdraw()        
		
		#activate onclick
		self.canvas.bind('<Button-1>', self.click)
		self.canvas.bind('<ButtonRelease-1>', self.unclick)
			
		
		
	"""AUXILIAR METHODS"""
	##	calcPosition(self, x, y): calculates the coordinates, given x and y, taking into
	#	account scrolls offsets.
	#
	#	@param x: Position in screen of the X axis
	#	@param y: Position in screen of the Y axis
	#
	#	@return A list with the new coordinates
	def calcPosition(self, x, y):
		size = self.cvimg.shape
		
		scrollX = self.xscrollbar.get()
		scrollY = self.yscrollbar.get()
		newX = scrollX[0] * size[1] + x
		newY = scrollY[0] * size[0] + y

		return (newX, newY)
	
	##	changeImgCanvas(self): changes the image showing to the new one selected.
	def changeImgCanvas(self):
		#Error management
		if self.scorePath == "":
			return
		"""
		ext = self.scorePath.split(".")
		tam = len(ext) - 1
		if ext[tam] != 'jpg' and ext[tam] != 'png' and ext[tam] != 'bmp':
			tkMessageBox.showwarning(
				"Open file",
				"Cannot open extension %s.\n Try .jpg, .png, .bmp" % ext[1]
			)
			return
			"""
		
		#Clean window
		for w in widgetList:
			w.pack_forget()        
		
		#Open score image
		self.cvimg = cv2.imread(self.scorePath, 0)        
		img = PIL.Image.fromarray(self.cvimg)
		self.imgtk = PIL.ImageTk.PhotoImage(image=img)        
		
		#Create scroll
		self.xscrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
		self.xscrollbar.grid(row=1, column=0, sticky=tk.E + tk.W)
		
		self.yscrollbar = tk.Scrollbar(self.frame)
		self.yscrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)   
		
		#Update canvas and scroll
		self.canvas.itemconfigure(self.item, image=self.imgtk, anchor=tk.NW)
		self.canvas.configure(scrollregion=self.canvas.bbox('all'), xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
		self.xscrollbar.config(command=self.canvas.xview)
		self.yscrollbar.config(command=self.canvas.yview)
		
		#resize window
		if self.root.winfo_screenwidth() < self.cvimg.shape[1]:
			width = self.root.winfo_screenwidth()
		else:
			width = self.cvimg.shape[1]
		if self.root.winfo_screenheight() < self.cvimg.shape[0]:
			height = self.root.winfo_screenheight()
		else:
			height = self.cvimg.shape[0]
			
		self.root.geometry('%dx%d' % (width, height))

		
	##	adjustArea(self, pos): reduces the pattern selected by the user so that it only
	#	covers the head of the note. 
	#
	#	@param pos: Coordinates of the image where the user has clicked
	#
	#	@return The new area.
	def adjustArea(self, pos):
		
		[d, t] = self.scoreG.getStaveParams()
		minY = pos[1] - (d/1.5 + 2*t)
		maxY = pos[1] + (d/1.5 + 2*t)
		minX = pos[0] - (d/1.5 + 2*t)
		maxX = pos[0] + (d/1.5 + 2*t)
		
		area = self.cvimg[minY:maxY, minX:maxX].copy() #img[y1:y2, x1:x2]        
		[row, col] = area.shape
		
		cv2.imwrite('/home/alumnoeps/Desktop/recuadro.jpg', area)
	
		#above
		sum = 0
		above = 0
		stop = 0
		for r in range(0, row):
			if stop == 1:
				above += 2
				break
			
			for c in range(0, col):
				if area[r][c] < THRESHOLD:
					sum += 1
					if sum > 2*t:
						above = r 
						#watch out stave lines
						if area[above][0] < THRESHOLD or area[above][col-1] < THRESHOLD:
							above = r + t
						else:
							stop = 1
						break
				else:
					sum = 0
			
		#below
		sum = 0
		below = 0
		stop = 0
		for r in range(row-1, 0, -1):
			if stop == 1:
				below -= 2
				break
			
			for c in range(0, col):
				if area[r][c] < THRESHOLD:
					sum += 1    
					if sum > 2*t:
						below = r
						#watch out stave lines
						if area[below][0] < THRESHOLD or area[below][col-1] < THRESHOLD:
							below = r - t
						else:
							stop = 1
						break
				else:
					sum = 0
			
		#left
		sum = 0
		left = 0
		for c in range(0, col):
			if left != 0:
				break
			
			for r in range(0, row):
				if area[r][c] < THRESHOLD:
					sum += 1   
					if sum > 1.5*t:                        
						left = c - t
						break
				else:
					sum = 0
					
			
		#right
		sum = 0
		right = 0
		for c in range(col-1, 0, -1):
			if right != 0:
				break
			
			for r in range(0, row):
				if area[r][c] < THRESHOLD:
					sum += 1    
					if sum > 1.5*t:
						right = c + t
						break
				else:
					sum = 0
			
		#save new area
		if below - above > d - d/3 and right - left > d - d/3:
			area = area[above:below, left:right].copy() #img[y1:y2, x1:x2]
		cv2.imwrite('/home/alumnoeps/Desktop/ajuste.jpg', area)
		return area
		
		
		
		
		
		
		
