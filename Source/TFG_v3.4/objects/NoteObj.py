##  Created on 
#   @author: Monica Villanueva Aylagas

import cv2

WHITE = 255
DIV_SHORT = 1.5
DIV_LONG = 1.9
THRESHOLD = 18 #15 #Horizontal Threshold 
THRESV = 50 #Vertical Threshold


##  Intermediate representation of a note
#
#   @author Monica Villanueva Aylagas
#   @date 11/10/2014
class NoteObj(object):

    ##  Constructor
    def __init__(self):        
        self.pitch = None
        self.accidental = None
        self.rhythm = None
        self.dot = None
        
    
        
    """
    def isStem(self, sum, tam):
        
        # find line
        if (sum < (WHITE * tam / DIV_LONG)):
            return 1
        elif (sum < (WHITE * tam / DIV_SHORT)):
            return 0.5
        
        # find blank
        else:
            return 0



    findPossibleStem(self, area): returns the areas where is possible to find stems
    
    area: stave area
    def findPossibleStem(self, area):
        [row, col] = area.shape
        black_flag = 0
        cont = 0
        stemArea = []
        
        #Scan the image
        for c in range(0, col):
            sum = 0
            for r in range (0, row):
                sum += area[r][c]
            
            #Find vertical line (stem/bar)
            ret = self.isBar(sum, row, black_flag)
            black_flag = ret[1] 
            
            if (ret[0] == 1):
                cont += 1
                subarea = area[0:row, c-PAD:c+PAD] #roi = gray[y1:y2, x1:x2]
                stemArea.append(subarea)
                
        
        print 'Numero de barras de compas + plicas: ', cont
        
        #for i in range (0, len(stemArea)):
        #    [subrow, subcol] = stemArea[i].shape
        #    cv2.rectangle(area, (stemArea[i][0], 0), (stemArea[i][subcol], row), (155,255,255), 2)
        
        
        cv2.imwrite('pruebaPlicas.png',stemArea[3])
        
        return stemArea
    """
    

    ##  isStave(self, row, upper, d, t): Test if a line is part of a stave or not.
    #
    #   @param row: line to test
    #   @param upper: First line of a stave
    #   @param d: distance between stave lines
    #   @param t: stave thickness
    #
    #   @return True if the line is part of a stave
    def isStave(self, row, upper, d, t):
        
        for i in range (-2,7):  #broaden for additional notes
            if row == upper + i*t + i*d:
                return True
            for j in range (1,t):
                if row == upper + i*t + i*d + j:
                    return True
            
        return False


    ##  recogPitch(self, head_centre, upper, d, t): recognizes a note's pitch given its area and fills the structure
    #
    #   @param head_centre: center point of the head on the Y axis
    #   @param upper: upper line of the stave
    #   @param d: distance between stave lines
    #   @param t: stave thickness
    def recogPitch(self, head_centre, upper, d, t):
        
        PAD = d/4
               
        #above stave
        if (head_centre < upper - 5*(d + 1) + t + PAD and head_centre > upper - 5*(d + 1) - PAD):
            self.pitch = 'b6' #si
        elif(head_centre <= upper - 4*(d + 1) - PAD and head_centre >= upper - 5*(d + 1) + t + PAD):
            self.pitch = 'a6' #la    
        elif (head_centre < upper - 4*(d + 1) + t + PAD and head_centre > upper - 4*(d + 1) - PAD):
            self.pitch = 'g6' #sol
        elif(head_centre <= upper - 3*(d + 1) - PAD and head_centre >= upper - 4*(d + 1) + t + PAD):
            self.pitch = 'f6' #fa
        elif (head_centre < upper - 3*(d + 1) + t + PAD and head_centre > upper - 3*(d + 1) - PAD):
            self.pitch = 'e6' #mi
        elif(head_centre <= upper - 2*(d + 1) - PAD and head_centre >= upper - 3*(d + 1) + t + PAD):
            self.pitch = 'd6' #re
        elif (head_centre < upper - 2*(d + 1) + t + PAD and head_centre > upper - 2*(d + 1) - PAD):
            self.pitch = 'c6' #do
        elif(head_centre <= upper - (d + 1) - PAD and head_centre >= upper - 2*(d + 1) + t + PAD):
            self.pitch = 'b5' #si        
        elif (head_centre < upper - (d + 1) + t + PAD and head_centre > upper - (d + 1) - PAD):
            self.pitch = 'a5' #la
        elif(head_centre <= upper - PAD and head_centre >= upper - (d + 1) + t + PAD):
            self.pitch = 'g5' #sol
        
        #stave
        elif (head_centre < upper + t + PAD and head_centre > upper - PAD):
            self.pitch = 'f5' #fa
        elif(head_centre <= upper + (d + 1) - PAD and head_centre >= upper + t + PAD):
            self.pitch = 'e5' #mi
        elif (head_centre < upper + (d + 1) + t + PAD and head_centre > upper + (d + 1) - PAD):
            self.pitch = 'd5' #re            
        elif(head_centre <= upper + 2*(d + 1) - PAD and head_centre >= upper + (d + 1) + t + PAD):
            self.pitch = 'c5' #do
        elif(head_centre < upper + 2*(d + 1) + t + PAD and head_centre > upper + 2*(d + 1) - PAD):
            self.pitch = 'b4' #si  
        elif(head_centre <= upper + 3*(d + 1) - PAD and head_centre >= upper + 2*(d + 1) + t + PAD):
            self.pitch = 'a4' #la
        elif(head_centre < upper + 3*(d + 1) + t + PAD and head_centre > upper + 3*(d + 1) - PAD):
            self.pitch = 'g4' #sol         
        elif(head_centre <= upper + 4*(d + 1) - PAD and head_centre >= upper + 3*(d + 1) + t + PAD):
            self.pitch = 'f4' #fa
        elif(head_centre < upper + 4*(d + 1) + t + PAD and head_centre > upper + 4*(d + 1) - PAD):
            self.pitch = 'e4' #mi 
        elif(head_centre <= upper + 5*(d + 1) - PAD and head_centre >= upper + 4*(d + 1) + t + PAD):
            self.pitch = 'd4' #re
            
        #below stave
        #""" comprobar que sigue dentro del recuadro """
        elif(head_centre < upper + 5*(d + 1) + t + PAD and head_centre > upper + 5*(d + 1) - PAD):
            self.pitch = 'c4' #do  
        elif(head_centre <= upper + 6*(d + 1) - PAD and head_centre >= upper + 5*(d + 1) + t + PAD):
            self.pitch = 'b3' #si
        elif(head_centre < upper + 6*(d + 1) + t + PAD and head_centre > upper + 6*(d + 1) - PAD):
            self.pitch = 'a3' #la 
        elif(head_centre <= upper + 7*(d + 1) - PAD and head_centre >= upper + 6*(d + 1) + t + PAD):
            self.pitch = 'g3' #sol
        elif(head_centre < upper + 7*(d + 1) + t + PAD and head_centre > upper + 7*(d + 1) - PAD):
            self.pitch = 'f3' #fa 



    ##  recogRhythm(self, note, head_centre, upper, d, t): recognizes a note's rhythm given its area and fills the structure
    #
    #   @param note: note area
    #   @param head_centre: center point of the head on the Y axis
    #   @param upper: upper line of the stave
    #   @param d: distance between stave lines
    #   @param t: stave thickness
    def recogRhythm(self, note, head_centre, upper, d, t):
        
        PADH = 3*t
        PADV = 3*d + d/2
        PADR = round(d/3)
        
        [row, col] = note.shape
        lower = upper + 5*t + 4*d 
        zero = 0       
        
        leftLimit = col
        rightLimit = 0

        for c in range(0, col):
            if leftLimit != col:
                break
            for centres in range (int(head_centre-d/2), int (head_centre+d/2)):
                if self.isStave(centres, upper, d, t) == True:
                    continue
                if note[centres][c] < THRESHOLD and note[centres][0] > THRESHOLD and note[centres][1] > THRESHOLD:    #if it's black 
                    if note[centres][c+1] > THRESHOLD or note[centres+1][c] > THRESHOLD or note[centres-1][c] > THRESHOLD:  #if white, then it was noise
                        continue         
                    leftLimit = c 
                    break     
            
        for c in range(col-1, leftLimit, -1):
            if rightLimit != 0:
                break
            for centres in range (int(head_centre-d/2), int(head_centre+d/2)): 
                if self.isStave(centres, upper, d, t) == True:
                    continue
                if note[centres][c] < THRESHOLD and note[centres][col-1] > THRESHOLD and note[centres][col-2] > THRESHOLD:    #if it's black
                    if note[centres][c-1] > THRESHOLD or note[centres+1][c] > THRESHOLD or note[centres-1][c] > THRESHOLD:  #if white, then it was noise
                        continue                    
                    rightLimit = c-1 
                    break
        
           
        #Vertical limits 
        if head_centre < upper + PADV:
            row = int (lower + PADV)
        elif head_centre > lower - PADV:
            zero = int (upper - PADV)
        else:
            row = int (lower + PADV)
            zero = int (upper - PADV)
            
        subarea = note[zero:row, 0:col].copy() #img[y1:y2, x1:x2] 
        cv2.imwrite('subarea.png', subarea) 
                      
        #Find stem top/bottom
        end = None
        if leftLimit == col:
            leftLimit -= 1
        stem = leftLimit
        
        while 1:            
            sum = 0
            white = 0
            for r in range (head_centre, row):    #down
                try:
                    if note[r][stem] < THRESV:
                        sum = sum
                except IndexError:
                    print r, stem
                    
                if note[r][stem] < THRESV:
                    white = 0
                    sum += 1
                    if sum > d and end < r:
                        end = r
                else:
                    sum = 0
                    white += 1
                    if white > d:
                        break
            sum = 0
            white = 0
            if (end == None):
                for r in range (head_centre, zero, -1):    #up
                    if (note[r][stem] < THRESV):
                        white = 0
                        sum += 1
                        if sum > d:
                            end = r
                    else:
                        sum = 0
                        white += 1
                        if white > d:
                            break 
            #end condition            
            if (end == None and stem == rightLimit) or (end != None and stem != leftLimit):
                break            
            #change of possible stem
            if stem == leftLimit and leftLimit != col - 1:
                stem = leftLimit + 1
            elif end == None and stem == leftLimit + 1 or stem == col - 1:
                stem = rightLimit  
            
        left = stem - PADH
        right = stem + PADH 
        
        #Order range
        if (end > head_centre):
            first = head_centre + int(d/1.5)
            last = end
        else:
            first = end
            last = head_centre - int(d/1.5)
        #Extreme case (end not found)    
        if first == None:
            first = zero
        
        #Search for flags/beams (both sides of the stem)
        #Left
        sum = 0
        lbeams = 0
        for r in range (first, last):
            
            #if head, miss
            if (r > head_centre - (d/2) and r < head_centre + (d/2)):
                continue
            
            # if black and stem (beam is attached to stem)
            if (note[r][left] < THRESV):
                sum += 1
            
            #if white
            else:
                #compare if grater than thickness
                if (sum >= PADR):
                    lbeams += 1
                sum = 0
        
        #compare last one (eighth)
        if (sum >= PADR):
            lbeams += 1
                
        #Right
        sum = 0
        rbeams = 0
        for r in range (first, last):
            
            #if head, miss
            if (r > head_centre - (d/2) and r < head_centre + (d/2)):
                continue
            
            # if black and stem (beam is attached to stem)
            if (note[r][right] < THRESV):
                sum += 1
            
            #if white
            else:
                #compare if grater than thickness
                if (sum >= PADR):
                    rbeams += 1
                sum = 0
        
        #compare last one (eighth)        
        if (sum >= PADR):
            rbeams += 1
                
        #Save the minor rhythm (mayor value) 
        if (lbeams < rbeams):
            flags = rbeams
        else:
            flags = lbeams
            
        #Conversion
        if flags == 0:
            self.rhythm = 'quarter'
        elif flags == 1:
            self.rhythm = 'eighth'
        elif flags == 2:
            self.rhythm = '16th'
        elif flags == 3:
            self.rhythm = '32nd'
        #assume that there is nothing smaller
        elif flags > 3:
            self.rhythm = '64th'
        
        
        