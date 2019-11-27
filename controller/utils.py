

def nameToUpper(name):
    newWord = True
    newName = ''
    for i in range(0, len(name)):
        #Capitalize all first letters
        if(newWord and name[i].isalpha()):
            newName += name[i].upper()
            newWord = False

        #Reset newWord after a space character
        elif(name[i] == ' '):
            newName += name[i]
            newWord = True
        
        #Otherwise just include the original char
        else:
            newName += name[i]
    
    return newName