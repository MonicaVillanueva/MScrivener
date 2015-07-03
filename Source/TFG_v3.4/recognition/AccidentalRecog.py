THRESHOLD = 50

import cv2

##   Recognizes accidentals and determines its type
#
#   @author Monica Villanueva Aylagas
#   @date 16/01/2015
class AccidentalRecog(): 
    

    ##  Constructor
    def __init__(self):

        self.type = None
        
    ##  recogType(self, note, head_centre, upper, d, t): recognizes an accidental type given its area and fills the structure
    #
    #   @param acc: accidental area
    #   @param center: center point of the accidental on the Y axis
    #   @param d: distance between stave lines
    #   @param t: stave thickness
    #
    #   @return String with its type
    def recogType(self, acc, center, d, t):
        
        [row, col] = acc.shape        
        edge = -1
        
        #Find accidental edge (black)
        for c in range (col-1, 0, -1):
            if acc[center][c] < THRESHOLD:
                edge = c
                break
            
        
        if edge == -1:
            return None
        
        #if black up -> sharp
        if acc[center - d][edge] < THRESHOLD:
            return 'sharp'
        
        #if not, look down; if black -> natural
        if acc[center + d][edge] < THRESHOLD:
            return 'natural'
        
        #if not -> flat
        return 'flat'
    
    
    ##  findAccidental(self, area, headX, headY, d): find an accidental given the stave area
    #   and the position of the note head.
    #
    #   @param area: stave area
    #   @param headX: start point of the head on the X axis
    #   @param headY: center point of the head on the Y axis
    #   @param d: distance between stave lines
    #   @param t: stave thickness
    #
    #   @return 1 if finds accidental (0 if not) and the remaining area (in a list)
    def findAccidental(self, area, headX, headY, d, t):

        [row, col] = area.shape
        
        # Accidental is placed before the note
        for c in range (headX, headX - d/2, -1):
            #sum = 0
            if area[headY][c] < THRESHOLD and area[headY + 4*t][c] < THRESHOLD: 
                end = c + 2
                c -= 1
                
                black = 1
                while area[headY][c] < THRESHOLD:   #until white
                    if c < headX - d: 
                        return [0, area]
                    c -= 1
                    black += 1
                
                while area[headY][c] > THRESHOLD:   #until black again
                    if c < headX - d:
                        return [0, area]
                    c -= 1
                
                # if second black area is significantly larger than first is not an accidental
                if area[headY][c - 2*black] < THRESHOLD:  
                    return [0, area]
                        
                #save area
                begin = c-d/2
                accArea = area[0:row, begin: end].copy() #img[y1:y2, x1:x2]  
                cv2.imwrite('subarea.png',accArea)
                
                #Identify type
                self.type = self.recogType(accArea, headY, d, t)
                
                if self.type == None:
                    return [0, area]
                
                pair = (headY, begin)
                self.accCenter = pair
                
                cv2.rectangle(area, (begin, 0), (end, row), (255,255,255), -1) #delete accidental
                
                return [1, area]
            
        return [0, area]
            
            
            
            
        