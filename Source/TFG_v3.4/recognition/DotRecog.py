THRESHOLD = 50

import cv2

##  Finds dots in a stave
#
#   @author Monica Villanueva Aylagas
#   @date 24/01/2015
class DotRecog():    

    ## Constructor
    def __init__(self):



    ##  findDottedRhythm(self, area, headX, headY, upper, d, t): Recognizes dots in a stave.
    #
    #   @param area: stave area
    #   @param headX: start point of the head on the X axis
    #   @param headY: center point of the head on the Y axis
    #   @param upper: upper line of the stave
    #   @param d: distance between stave lines
    #   @param t: stave thickness
    #
    #   @return returns 1 if finds a dotted rhythm (0 if not) and 
    #   the remaining area (in a list)
    def findDottedRhythm(self, area, headX, headY, upper, d, t):
        
        [row, col] = area.shape
        
        line = 0
        #Near the stave lines there must be a space
        for i in range (7, -2,-1):  #broaden for additional notes
            if headY - 2*t > upper + i*t + i*d:
                line = upper + i*t + i*d
                break
            
        #set limits
        top = int(headY - d)
        if top < 0:
            top = 0
            
        bot = int(headY + d)
        if bot > row:
            bot = row   
        
        # Dot is placed after the note
        begin = -1
        for c in range (headX + 2*d, int(headX + 2.5*d)): #headX + 3*d
            
            #if black near the stave line
            if area[line + 3*t][c] < THRESHOLD:
                return [0, area]                         
            
            sum = 0            
            for r in range (top, bot):            
                if area[r][c] < THRESHOLD: 
                    sum += 1
                    begin = c - 2  
                #if black near the stave line
                for intern in range (c, int(headX + 2.5*d)):
                    if area[line + 3*t][intern] < THRESHOLD:
                        return [0, area]
            
            if sum - 3*t >= d/3 and sum - 3*t <= d/1.5: #d/2
                #save area            
                end = c + d/1.5
                dotArea = area[0:row, begin:end].copy() #img[y1:y2, x1:x2]  
                cv2.imwrite('subarea.png',dotArea)
                
                return [1, area]
        
        return [0, area]
        
        