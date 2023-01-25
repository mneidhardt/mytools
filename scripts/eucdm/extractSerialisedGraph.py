import sys
import csv

# This is a script to read a CSV file containing (potentially) all Data Element numbers along with 'column' presence info and cardinality.
# Specifically, the file has these columns:
# 1=Data element number This must be a unique columnx, and it must be sorted in ascending order.
# 2-10: Each of the H and I "columns" (or any other group of "columns" that are coupled in te EUCDM).
#       Columns 2-10 contain 'a' 'b', 'c' or nothing, as specified in the EUCDM.
# 11: Data element's cardinality in relation to Declaration level.
# 12: Data element's cardinality in relation to GS level.
# 13: Data element's cardinality in relation to SI level.
# 14: Codelist - either 'y', 'n' or empty.
# NB: Column 14 is not currently used in the script.
#
# From this I build a serialised graph for the chosen 'column', i.e. one of H1, H2,...H7,I1,I2.
# It's done by looping over the matrix once per cardinality column, and in that loop I loop once over all DataElements,
# thereby outputting the children of each level together.
# NB: It only produces a (fairly good) attempt at the serialised graph. 
# You must go over and check the resulting serialised graph.
#
#--------------------------------------------------------------------------------------------------------------------------

# Function to determine action when receiving a DE, given the previous one.
# Does not alter anything, but returns an 2-elem list:
# [0] = the number of end-of-child markers to print before the current data element.
# [1] = the number of end-of-child markers to print after the current data element.
# The [1] element is only used after the inner loop ends, in which case it can be used to print out EOC
# before the next round - i.e. before the artificial level is printed.
def determineAction(previous, current):
    if previous == '':
        previous = '00 00 000 000'

    # when comparing previous and current DENo, I want to be able to use both the string and
    # the integer version, so convert both here to lists of integers.
    prevI = [int(x) for x in previous.split()]
    currI = [int(x) for x in current.split()]

    if previous == '00 00 000 000' and currI[0] > 0 and currI[1] > 0 and currI[2] == 0 and currI[3] == 0:
        # print('# NB: OK, known situation.', previous, ' <---> ', current)
        return([0, 1])    # Transition 3, State 0->1
    elif previous == '00 00 000 000':
        print('# NB: Unknown situation 1.', previous, ' <---> ', current) # Dont know this state, so shout about it!
        return([0, 0])    # Unknown transition.
    elif previous[0:5] == current[0:5] and prevI[2] == 0 and prevI[3] == 0 and currI[2] > 0 and currI[3] == 0:
        return([0, 2]) # Transition 2, State 1->2
    elif previous[0:5] != current[0:5] and currI[2] == 0 and currI[3] == 0 and prevI[2] > 0 and prevI[3] == 0:
        return([2, 1])    # Transition 3, State 2->1
    elif previous[0:5] == current[0:5] and prevI[2] > 0 and prevI[3] == 0 and currI[2] > 0 and currI[3] == 0:
        return([1, 2]) # Transition 4, State 2->2
    elif previous[0:9] == current[0:9] and prevI[3] == 0 and currI[3] > 0:
        return([0, 3]) # Transition 5, State 2->3
    elif previous[0:9] == current[0:9] and prevI[3] > 0 and currI[3] == 0:
        return([1, 2]) # Transition 6, State 3->2
    elif previous[0:5] == current[0:5] and prevI[2] > 0 and prevI[3] > 0 and currI[2] > 0 and currI[3] == 0:
        return([2, 2]) # Transition 6, State 3->2
    elif previous[0:9] == current[0:9] and prevI[3] > 0 and currI[3] > 0:
        return([1, 3]) # Transition 7, State 3->3
    elif previous[0:5] != current[0:5] and prevI[2] > 0 and prevI[3] > 0 and currI[2] == 0 and currI[3] == 0:
        return([3, 1])  # Transition 8, State 3->1
    else:
        print('# NB: Unknown situation 2.', previous, ' <---> ', current) # Dont know this state, so shout about it!
        return([0, 0])

def readFile(filename):
    data = []

    with open(filename) as csvfile:
        crdr = csv.reader(csvfile, delimiter=';')
        for row in crdr:
            if len(row) == 0:   # or row[0].lstrip().startswith('#'):
                continue
            else:
                data.append([x.strip() for x in row])
    return data

# The function that does the main work.
# Args: data is the matrix outlined above, possibly with more columns.
# columnno: the column in the matrix for which you want fields, e.g. 7 if you want H7-fields.
# cardcolumns: the columns in which to look for cardinalities. The function's outer loop loops over these.
#-----------------------------------------------------------------------------------------------------------------
def extractSerialisedGraph(data, columnno, cardcolumns):
    indent = '    '
    for card in cardcolumns:        # Outer loop - over all the levels, i.e. Decl, GS, SI in this case.
        print(cardcolumns[card])
        previous = ''
        for row in data:
            if row[columnno] != '' and row[card] != '':
                action = determineAction(previous, row[0])      # Determine what to output.
                for i in range(0, action[0]):
                    print('!')

                cardinality = int(row[card])
                if cardinality == 1:
                    print(row[0])      # 1 is default cardinality, so I dont print it.
                else:
                    print(row[0] + '/' + row[card])

                previous = row[0]
        for i in range(0, action[1]):
            print('!')

if __name__ == "__main__":
    filename = sys.argv[1] # Name of file containing relations.
    columnname = sys.argv[2];              # One of H1,H2,H3,H4,H5,H6,H7,I1,I2.
    # Cardcolumns: keys are index into the columns in filename, in the order you want them to appear.
    # In the case of H7, there are only 3 levels, 1=Declaration, 6=Good Shipment, 7=SI (GAGI)
    # This variable just tells the function which index to use to find cardinality, and which name to use in the tree.
    cardcolumns = {}
    cardcolumns[10] = '1'
    cardcolumns[11] = '6'
    cardcolumns[12] = '7/9999'
    data = readFile(filename)
    headers = data.pop(0)
    # Find the index of the column containing the wanted 'column', i.e. message.
    columncol = headers.index(columnname)
    extractSerialisedGraph(data, columncol, cardcolumns)
