from music21 import stream
from music21 import metadata
from music21 import *
from objects import *

## Encapsule the writing into MusicXML using music21 library
#
#   @author Monica Villanueva Aylagas
#   @date 06/11/2014
class MusicXML(object):
    

    ##  Constructor
    def __init__(self):        
        self.measure_count = 0   #measure index
        self.r_count = 0         #rhythm counter in a measure
        self.timeSig = None      #current time signature
        self.measureAcc = []     #list of accidentals within a measure


    ##  write(self, path): writes a musicxml file in the chosen path
    #
    #   @param path: output path
    #   @param score: music21 object created with the information of the score
    def write(self, path, score):
        score.write(fp = path)

    ##  headerWriter(self, title, composer): writes in musicxml format a title and composer for de work.
    #   It also set the time signature and key signature for the score.
    #
    #   @param title: title of the work
    #   @param composer: music's composer
    #   @param timeSignature: time signature for the score (string)
    #   @param keySignature: key signature for the score (int)
    #
    #   @return Score object created with the information
    def headerWriter(self, title, composer, timeSignature, keySignature):
        
        #Create measure and part        
        m = stream.Measure()
        m.timeSignature = meter.TimeSignature(timeSignature)
        m.keySignature = key.KeySignature(keySignature)
        self.timeSig = timeSignature
        
        p = stream.Part()
        p.append(m)

        #Create score
        score = stream.Score()
        score.append(p)
        
        #Fill header
        score.insert(metadata.Metadata())
        score.metadata.movementName = title
        score.metadata.composer = composer
        
        return score


    ##  finalBarlineWriter(self,score): writes a final bar in the last measure of the score.
    #
    #   @param score: score object in which we are writing the final barline
    def finalBarlineWriter(self, score):
        
        #Get the last measure
        last = len(score.getElementsByClass('Part')[0].getElementsByClass('Measure'))
        m = score.getElementsByClass('Part')[0].getElementsByClass('Measure')[last-1]
        
        #Create the barline
        bl = bar.Barline(style='final', location='right')
        
        #Add the barline to the measure
        m.rightBarline = bl
    
    
    
    
    ##  keySigAlteration(self, key, pitch): change the accidental of a note based on the key signature.
    #
    #   @param key: key signature (int)
    #   @param pitch: note pitch
    #
    #   @return The accidental that modifies the note regarding the key signature.
    def keySigAlteration(self, key, pitch):
        #Get pitch
        p = pitch[:1]
        
        if key == 0:
            return
        
        if key > 0:        
            #Sharps
            if key >= 1 and p == 'f':
                return 'sharp'
            if key >= 2 and p == 'c':
                return 'sharp'
            if key >= 3 and p == 'g':
                return 'sharp'
            if key >= 4 and p == 'd':
                return 'sharp'
            if key >= 5 and p == 'a':
                return 'sharp'
            if key >= 6 and p == 'e':
                return 'sharp'
            if key >= 7 and p == 'b':
                return 'sharp'
        else:    
            #Flats
            if key <= -1 and p == 'b':
                return 'flat'
            if key <= -2 and p == 'e':
                return 'flat'
            if key <= -3 and p == 'a':
                return 'flat'
            if key <= -4 and p == 'd':
                return 'flat'
            if key <= -5 and p == 'g':
                return 'flat'
            if key <= -6 and p == 'c':
                return 'flat'
            if key <= -7 and p == 'f':
                return 'flat'


    ##  objWriter(self, score, note): Converts a object into a format understandable by the music21 library
    #   
    #   @param keySignature: keySignature for the score (int)
    #   @param part: music21 object in which we are 'writing'
    #   @param obj: obj (note, rest) which contains the information to write
    def objWriter(self, keySignature, part, obj):
        
        #Create note
        if isinstance(obj, NoteObj.NoteObj):
            o = note.Note(obj.pitch)
            o.duration.type = obj.rhythm
            
        
        #Create rest
        elif isinstance(obj, RestObj.RestObj):
            o = note.Rest()
            o.duration.type = obj.rhythm
            
        #Add dot
        if obj.dot:
            o.duration.dots = 1
        

        #update rhythm counter
        rhythm_conv = o.quarterLength
        
        #Control measure
        ts = self.timeSig.split('/')    #ts[0] numerator; ts[1] denominator
        if ts[1] == '1':
            denom = 4
        elif ts[1] == '2':
            denom = 2
        elif ts[1] == '4':
            denom = 1
        elif ts[1] == '8':
            denom = 0.5
        elif ts[1] == '16':
            denom = 0.25
        elif ts[1] == '32':
            denom = 0.125
        else:
            denom = 0.0625
        max = float(ts[0]) * denom
        
        if max <= self.r_count:
            #new measure
            self.measure_count += 1
            self.r_count = rhythm_conv
            part.append(stream.Measure())
            #clean the list of measureAcc
            self.measureAcc = []
        else:
            self.r_count += rhythm_conv 
            
        #Accidental must be after control measure because it's affected by the measure itself  
        #Update accidental   
        if isinstance(obj, NoteObj.NoteObj):
            if obj.accidental != None:
                o.pitch.accidental = obj.accidental
                #save pitch and accidental (if there is another note with the same 
                #pitch and it's not natural, then it has the same accidental)
                pair = [obj.pitch, obj.accidental]
                self.measureAcc.append(pair)
                """
                if any(pair for pair in self.measureAcc if  == 30) == False:   #contains
                    self.measureAcc.append(pair)
                """
                #TODO hacer una hash - cuidado si ya esta en la lista con otra alteracion?
            else:
                modified = False
                for pair in self.measureAcc:
                    #extract note
                    n = pair[0][0]
                    this = obj.pitch[0]
                    
                    if n == this:
                        o.pitch.accidental = pair[1]
                        modified = True
                        break   
                    
                if modified == False:
                    #FIXME
                    if obj.pitch == None:
                        obj.pitch = 'c5'
                    o.pitch.accidental = self.keySigAlteration(keySignature, obj.pitch)
                    
                    
                        
        
        #Append to the measure
        part.getElementsByClass('Measure')[self.measure_count].append(o)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        