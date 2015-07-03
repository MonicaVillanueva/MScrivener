import cv2

WHITE = 255
DIV = 2.65

##	Finds staves in a score and calculates its
#	line thickness and distance between lines
#
#	@author Monica Villanueva Aylagas
#	@date 26/09/2014
class StaveRecog:

	##  Constructor
	def __init__(self):        
		self.stavesAreas = []
		self.d = -1  #distance between lines
		self.t = 0  #line thickness
	
		self.t_list = []
		self.d_list = []
		
		
	##  isLine(self, sum, col): Determines if a line is part of a stave or not. 
	#    
	#   @param sum: sum of the array of pixels in a row
	#   @param col: number of colums
	#   @param black_flag: flag that point if the last line was a stave line or not
	#
	#   @return A list with 1 if it finds a stave line, 
	#   0 if not, and the value of the flag that points if the last line was black
	def isLine(self, sum, col, black_flag):
		l = []
		
		# find line
		if sum < (WHITE * col / DIV):
			#if the previus was line, miss
			if black_flag == 1:
				self.t += 1
				l.append(int(0))
			#if not, count
			else:
				self.t += 1
				black_flag = 1            
				l.append(int(1))
			
			l.append(int(black_flag))
			return l
		
		# find blank
		else:
			if (self.t != 0):
				self.t_list.append(self.t)
				self.t = 0
			black_flag = 0
			l.append(int(0))
			l.append(int(black_flag))
			return l
		
	
	##  findUpper(self, img): Finds the upper line of the stave
	#
	#   @param img: stave area
	#
	#   @return Vertical pixel where starts the upper line of the stave
	def findUpper(self, img):
		
		[row, col] = img.shape
		
		cont = 0
		upper = -1
		
		
		#Scan the image
		for r in range(0, row):
			sum = 0
			for c in img[r]:
				sum += c
			
			#Counts number of lines until 5 (stave)
			ret = self.isLine(sum, col, 0)
			cont = cont + ret[0]
			
			if (cont == 1 and upper == -1):  #upper line
				upper = r 
				return upper  
		
		
		
	
	##  findStave(self, img): Find and stores the staves of a image
	#
	#   @param img: analyzed image
	#
	#   @return The number of staves in the image
	def findStave(self, img):
		
		[row, col] = img.shape
		
		cont = 0
		start = 0
		end = 0
		space = 0
		black_flag = 0
		first_flag = 0
		other_flag = 0
		d_flag = 0
		
		#Scan the image
		for r in range(0, row):
			sum = 0
			for c in img[r]:
				sum += c
			
			#Counts number of lines until 5 (stave)
			ret = self.isLine(sum, col, black_flag)
			cont = cont + ret[0]
			black_flag = ret[1] 
				
			if (cont == 1 and first_flag == 0):    #first stave
				first_flag = 1
				start = r
			elif (cont == 1 and end != 0 and other_flag == 0):    #not the first stave
				other_flag = 1
				#Distribute space between staves
				space = (r - end) / 2
				#save area
				subarea = img[start - space:end + space, 0:col].copy() #img[y1:y2, x1:x2] 
				self.stavesAreas.append(subarea)
				#cv2.imwrite('penta1.png',subarea)
				#self.staves.append([start - space, end + space])
				start = r                
			elif (cont == 5):
				other_flag = 0
				end = r
				cont = 0
				
			#Space between
			if (cont == 1 or cont == 3):
				self.d += 1 
			elif ((cont == 2 or cont == 4) and self.d != -1):
				self.d_list.append(self.d)
				self.d = -1
			
		
		#Last stave
		subarea = img[start - space:end + space, 0:col].copy() #img[y1:y2, x1:x2] 
		self.stavesAreas.append(subarea)
		#self.staves.append([start - space, end + space])
		
		#Set d and t
		self.t = int (round (round (float (reduce(lambda x,y: x+y, self.t_list)) / float (len(self.t_list)), 1))) #average thikness
		self.d = int (round (float (reduce(lambda x,y: x+y, self.d_list)) / float (len(self.d_list)))) #average distance
		
		return len(self.stavesAreas)
	   
	
	
		