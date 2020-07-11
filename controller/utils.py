

def name_to_upper(name):
    new_word = True
    new_name = ''
    for i in range(0, len(name)):
        #Capitalize all first letters
        if(new_word and name[i].isalpha()):
            new_name += name[i].upper()
            new_word = False

        #Reset newWord after a space character
        elif(name[i] == ' '):
            new_name += name[i]
            new_word = True
        
        #Otherwise just include the original char
        else:
            new_name += name[i]
    
    return new_name