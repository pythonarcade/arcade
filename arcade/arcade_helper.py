##help file
##Here you will find functions made to help you program

def arcade_helper(function):
    function = function.upper()
    arcade_helper_search = open("helper_dictionary.txt", "r")
    for line in arcade_helper_search:
        if function in line: print(line)
    arcade_helper_search.close()
    
arcade_helper("print")
arcade_helper("while")
arcade_helper("draw_arc_outline")
arcade_helper("as")