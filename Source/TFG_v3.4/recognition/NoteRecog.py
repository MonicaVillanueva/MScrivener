
PAD = 3 #5 Mirar TAMAGNO RELATIVO:espacio de los pentagramas 

import cv2
import numpy as np

##   Finds notes in a stave
#
#	@author Monica Villanueva Aylagas
#	@date 04/10/2014
class NoteRecog:

	##	Constructor
	def __init__(self):
		self.noteAreas = []
		self.headCentres = []
		
		
		
	##	findHead(self, area, patron): Recognizes note heads give its pattern.
    #   The findings are store in the structure lists. 
	#
	#	@param area: stave area
	#	@param patron: patron to match
	#
	#	@return The number of heads that match the patron in the area.
	def findHead(self, area, patron):
		
		cont = 0
		find = 1
		end = -1
		[area_heigth, begin] = area.shape
		
		w, h = patron.shape[::-1]
		
		while(1):
			# Stop when there are no more heads 
			if (find == 0):
				return [cont, area]
				
			find = 0
			old_centre = -1
			
			# Template Matching
			res = cv2.matchTemplate(area, patron, cv2.TM_CCOEFF_NORMED)            
			threshold = 0.65    #0.65
			loc = np.where (res >= threshold)
			
			for pt in zip(*loc[::-1]):
				find = 1
				new_centre = ((pt[0] + w) + pt[0]) / 2
				
				#duplicate
				if (abs(old_centre - new_centre) < w or old_centre > new_centre): 
					continue
				
				old_centre = new_centre
				
				#update end
				begin = pt[0]
				end = (pt[0] + w)
				cont += 1
				
				#save area
				subarea = area[0:area_heigth, begin-PAD:end+PAD].copy() #img[y1:y2, x1:x2]  
				#pair = (subarea, begin-PAD)        
				#self.noteAreas.append(pair)
				self.noteAreas.append(subarea)
				#save headcentre
				centre_y = ((pt[1] + h) + pt[1]) / 2  
				pair = (int(centre_y), int(begin-PAD))  
				self.headCentres.append(pair) 
				cv2.rectangle(area, (begin-PAD, 0), (end+PAD, area_heigth), (255,255,255), -1) #delete note
	   
						   
		