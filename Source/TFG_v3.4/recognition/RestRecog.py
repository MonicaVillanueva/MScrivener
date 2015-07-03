THRESHOLD = 50
PAD = 5

import cv2

##  Finds rests in a stave and recognizes it rhythm
#
#   @author Monica Villanueva Aylagas
#   @date 14/01/2015
class RestRecog:

    ##  Constructor
    def __init__(self):
        self.restAreas = []
        self.centres = []  
        self.rhythm = []
        
    
    
    ##  findWholeHalf(self, area, searchLine, upper, d, t): Recognizes whole and half rests.
    #   The findings are store in the structure lists. 
    #
    #   Note: Assumed that any thing remaining is a rest; no small notes.
    #
    #   @param area: stave area
    #   @param start: column where begin search. Avoids clef and key signature
    #   @param searchLine: row in which we are searching (whole: under 2 stave line; half: over 3 stave line)
    #   @param upper: upper line of the stave
    #   @param d: distance between stave lines
    #   @param t: stave thickness
    #
    #   @return The stave area edited (without the found rests)
    def findWholeHalf(self, area, start, searchLine, upper, d, t): 
        
        [row, col] = area.shape
        
        sum = 0
        begin = 0
        c_aux = 0
        for c in range(start, col):
            if c_aux > c:
                c = c_aux
                
            #find black in searchLine and white in other places
            if area[searchLine][c] < THRESHOLD and area[searchLine - d + 2*t][c] > THRESHOLD:
                sum += 1
                begin = c
                c += 1
                                
                #while black in searchLine and white in other places
                while area[searchLine][c] < THRESHOLD and area[searchLine - d + 2*t][c] > THRESHOLD and c < col:
                    sum += 1
                    c += 1
                
                end = c
                c_aux = c
                
            else:
                sum = 0
                begin = 0
                
            #wide enough
            if d <= sum < 2*d: # sum >= d
                #save area
                subarea = area[0:row, begin-PAD:end+PAD].copy() #img[y1:y2, x1:x2]  
                self.restAreas.append(subarea)
                cv2.imwrite('subarea.png',subarea)
                if upper + 2*t + d + 1 == searchLine:
                    self.rhythm.append('whole')
                    pair = (searchLine, begin-PAD) 
                else:
                    self.rhythm.append('half')
                    pair = (searchLine, begin-PAD)
                self.centres.append(pair)
                
                cv2.rectangle(area, (begin-PAD, 0), (end+PAD, row), (255,255,255), -1) #delete rest
                
        return area 
    
    
    
    ##  findQuarterOrSmaller(self, area, searchLine): Recognizes quarter rests 
    #   or with a smaller vale. The findings are store in the structure lists.
    #
    #   Note: Assumed that any thing remaining is a rest; no small notes
    #
    #   @param area: rest area
    #   @param searchLine: row in which we are searching (between 3-4)
    #   @param width: consecutive black pixels that must repeat for smallers rests
    #   @param d: distance between stave lines
    #   @param t: stave thickness
    def findQuarterOrSmaller(self, area, searchLine, width, d, t): 
        
        [row, col] = area.shape
        
        begin = 0
        black = 0
        end = 0
        for c in range(begin, col):
            if area[searchLine][c] < THRESHOLD:
                black += 1
                end = c
            elif black != 0:
                break


        if width - 2*t < black < width + 2*t:
            #semicorchea o mas peque
            self.rhythm.append('16th')
        
        elif begin - 3*t <= end - black <= begin + 3*t: 
            self.rhythm.append('quarter')
        else:
            self.rhythm.append('eighth')
            
            
            
    ##  noise(self, area, line, col, d): Distinguish if there is noise. 
    #
    #   @param area: stave area
    #   @param line: row in which we are searching
    #   @param col: column around which we must look
    #   @param d: distance between stave lines
    #
    #   @return True if noise is found       
    def noise(self, area, line, col, d):
        begin = col - d
        end = col + d
        
        for c in range(begin, end):
            if area[line][c] < THRESHOLD:
                return True
        return False
    
              
    
    ##  findRest(self, area): Find any kind of rest in a stave 
    #
    #   Note: Assumed that any thing remaining is a rest; no small notes.
    #
    #   @param area: stave area
    #   @param keySig: number of accidentals in the signature
    #   @param upper: upper line of the stave
    #   @param d: distance between stave lines
    #   @param t: stave thickness
    #
    #   @return The number of rests found in the area
    def findRest(self, area, keySig, upper, d, t):   
        
        [row, col] = area.shape
        
        #Find stave's start
        start = 0
        for c in range(0, col):
            if area[upper][c] < THRESHOLD:
                start = c
                break
            
        #avoid clef
        start += 3*d
        #avoid key signature
        start += abs(keySig)*d
        
        #line5 = int(upper + 4*t + 4*d)   
        
        #Whole (under 2 line)
        line2 = int(upper + 2*t + d)        
        cut = self.findWholeHalf(area, start, line2+2*t, upper, d, t)
        
        #Half (over 3 line)
        line3 = int(upper + 2*t + 2*d)        
        cut = self.findWholeHalf(cut, start, line3-2*t, upper, d, t)  
        
        #Quarter (between 2-3 lines)        
        between = line2 + (line3 - line2)/2  
        
        black = 0
        width = 0
        end = 0 
        for c in range(start, col):
            if cut[between][c] < THRESHOLD:
                black += 1
                end = c
            else:
                if d/2 < black < 1.5*d:   #1.5 por 2
                    width = black
                    black = 0
                    
                    #Mind noise
                    if self.noise(area, upper + 2*t, c, d):
                        continue

                    #save area
                    subarea = cut[0:row, end-width-PAD:end+PAD] 
                    cv2.imwrite('subarea.png', subarea)
                    self.restAreas.append(subarea)
                    pair = (between, end-width-PAD) 
                    self.centres.append(pair)
                    self.findQuarterOrSmaller(subarea, between + d + t, width, d, t)
                    cv2.rectangle(cut, (end-width-PAD, 0), (end+PAD, row), (255,255,255), -1) #delete rest
                else:
                    black = 0
        
        return len(self.restAreas)
        
        
        
        
        
        
        
        