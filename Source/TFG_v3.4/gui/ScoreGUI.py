import cv2
from recognition import *
from objects import *
from writer import *

##  Manages the flow of the recognition process, calling the
#   rest of the modules.
#
#	@author Monica Villanueva Aylagas
#	@date 08/02/2015
class ScoreGUI(object):
    
    ##  Constructor
    def __init__(self, root, cvimg):
        self.root = root
        
        #Recognize stave
        """Upload image"""
        self.sheet = StaveRecog.StaveRecog()  
        self.staveTotal = self.sheet.findStave(cvimg)
        
        """Get status label"""
        #ls = self.root.winfo_children()
        self.status = self.root.winfo_children()[4]
        
        txt = 'Number of staves found: ' + str(self.staveTotal)
        self.status.configure(text=txt)
        self.root.update()
        
    ##  getStaveParams(self): Getter for the thickness and
    #   distance between lines of a stave.
    #
    #   @return List containing the thickness and
    #   distance between lines
    def getStaveParams(self):
        ls = [self.sheet.d, self.sheet.t]
        return ls
    
    ##  start(self, spinValues, patterns, savePath):
    #
    #   @param spinValues: List containing the time signature, 
    #   and the key signature
    #   @param patterns: List containing patterns for whole,
    #   half and back notes
    #   @param savePath: Output path for the xml
    def start(self, spinValues, patterns, savePath):

        whole, half, black = patterns
        
        """Configure XML"""
        writer = MusicXML.MusicXML()
        timeSig = spinValues[0] + '/' +spinValues[1]
        keySig = int(spinValues[2])
        score = writer.headerWriter('OMR TFG', 'Monica Villanueva', timeSig, keySig)  
        
        
        
        staveNum = 0
        """Recognition"""
        for stave_area in self.sheet.stavesAreas:
            
            staveNum += 1            
            txt = 'Analyzing stave ' + str(staveNum) + '/' + str(self.staveTotal)
            self.status.configure(text=txt)
            self.root.update()
        
            obj_list = []   #one per stave
            cut = stave_area
            
            """ Find upper line of the current stave_area"""
            upper = self.sheet.findUpper(cut)
            #cv2.imwrite('penta1.png',stave_area)
            
            """NOTES"""
            stave = NoteRecog.NoteRecog()
            
            """Whole"""
            if whole != None:
                stave.noteAreas = []  
                stave.headCentres = []   
                [cont, cut] = stave.findHead(cut, whole)
                print 'Numero de cabezas redondas encontrados: ', cont
                
                
                """Pitch & rhythm"""
                cont = -1
                for i in stave.noteAreas:
                    cont += 1
                    note = NoteObj.NoteObj()
                    note.recogPitch(stave.headCentres[cont][0], upper, self.sheet.d, self.sheet.t)
                    note.rhythm = 'whole'
                    
                    # Save noteObj 
                    pair = (note, stave.headCentres[cont])
                    obj_list.append(pair)
            
            """Half"""
            if half != None:    
                stave.noteAreas = []  
                stave.headCentres = []    
                cv2.imwrite('half.png',half)
                [cont, cut] = stave.findHead(cut, half)
                print 'Numero de cabezas blancas encontrados: ', cont
                cv2.imwrite('cut.png',cut)
                
                """Pitch & rhythm"""  
                cont = -1
                for i in stave.noteAreas:
                    cont += 1
                    note = NoteObj.NoteObj()
                    note.recogPitch(stave.headCentres[cont][0], upper, self.sheet.d, self.sheet.t)
                    note.rhythm = 'half'                
                                
                    # Save noteObj
                    pair = (note, stave.headCentres[cont])
                    obj_list.append(pair)
                    
                    
            """Black"""
            if black != None: 
                stave.noteAreas = []  
                stave.headCentres = []     
                [cont, cut] = stave.findHead(cut, black)
                print 'Numero de cabezas negras encontrados: ', cont
                cv2.imwrite('cut.png',cut)                
                
                """Pitch & rhythm"""
                cont = -1
                for i in stave.noteAreas:
                    cont += 1
                    note = NoteObj.NoteObj()
                    cv2.imwrite('nota.png', stave.noteAreas[cont])
                    note.recogPitch(stave.headCentres[cont][0], upper, self.sheet.d, self.sheet.t)
                    note.recogRhythm(stave.noteAreas[cont], stave.headCentres[cont][0], upper, self.sheet.d, self.sheet.t)
                    
                    # Save noteObj 
                    pair = (note, stave.headCentres[cont])
                    obj_list.append(pair)
                    
                    
            """ACCIDENTAL"""
            cont = -1
            for pair in obj_list:
                cont += 1
                headC = pair[1]
                note = pair[0]
                res = 0
                # Search for accidentals
                acc = AccidentalRecog.AccidentalRecog()
                [res, cut] = acc.findAccidental(cut, headC[1], headC[0], self.sheet.d, self.sheet.t)
                if res == 1: 
                    # Modify note
                    note.accidental = acc.type 
                        
                    
            """RESTS"""
            stave = RestRecog.RestRecog()   
            cv2.imwrite('cut.png',cut)
            print 'Numero de silencios encontrados: ', stave.findRest(cut, keySig, upper, self.sheet.d, self.sheet.t)
            
            """Rhythm"""
            cont = -1
            for i in stave.restAreas:
                cont += 1
                rest = RestObj.RestObj()
                cv2.imwrite('nota.png', stave.restAreas[cont])
                rest.rhythm = stave.rhythm[cont]
                
                # Save restObj 
                pair = (rest, stave.centres[cont])
                obj_list.append(pair)
                
            """DOTTED RHYTHMS"""
            cont = -1
            for pair in obj_list:
                cont += 1
                headC = pair[1]
                obj = pair[0]
                res = 0
                # Search for dotted rhythms
                dot = DotRecog.DotRecog()
                [res, cut] = dot.findDottedRhythm(cut, headC[1], headC[0], upper, self.sheet.d, self.sheet.t)
                if res == 1: 
                    # Modify note
                    obj.dot = True
            
            
            #Sort notes by position (X axis)
            obj_list.sort(key=lambda tup: tup[1][1])   
        
        
        
            #solo  hay una parte (voz de instrumento)
            cont = -1
            for i in obj_list:
                cont += 1
                writer.objWriter(keySig, score.getElementsByClass('Part')[0], obj_list[cont][0])
                
        
        txt = 'Writting XML '
        self.status.configure(text=txt)
        self.root.update()        
        #Add final barline
        writer.finalBarlineWriter(score)
        
        writer.write(savePath, score)
        txt = 'Done!'
        self.status.configure(text=txt)
        self.root.update()
    
        
        
        
        
        
        
        
        
        