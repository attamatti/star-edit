#!/usr/bin/python
##############################################
### FETCH COPY - (fbsmi2016-04-13 16:15:30.631630) - download a fresh copy if necessary
##############################################

# AKA starfucker.py
# edit individual columns in a star file 


import sys

#------- function test if string is a number --------------------------#
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
#-----------------------------------------------------------------------

###---------function: read the star file get the header, labels, and data -------------#######
def read_starfile(f):
    alldata = open(f,'r').readlines()
    labelsdic = {}
    backlabelsdic = {}
    data = []
    header = []
    for i in alldata:
        if '#' in i:
            labelsdic[i.split('#')[0]] = int(i.split('#')[1])-1
            backlabelsdic[int(i.split('#')[1])-1] = i.split('#')[0]
        #print i.split()
        if len(i.split()) > 3:
            data.append(i.split())
        if len(i.split()) < 3:
            header.append(i.strip("\n"))
    return(labelsdic,header,data,backlabelsdic)
#---------------------------------------------------------------------------------------------#

#------ function: write all of the numbers in the fortran format ---------------------------#
def make_pretty_numbers(dataarray):
    prettyarray = []
    for line in dataarray:
        linestr = ""
        for i in line:
            if is_number(i):
                i = str(i)
                count = len(i.split('.'))
                if count > 1:
                    i = float(i)
                    if len(str(i).split('.')[0]) > 5:
                        linestr= linestr+"{0:.6e} ".format(i)
                    else:
                        linestr= linestr+"{0:12.6f} ".format(i)
                else:
                    linestr= linestr+"{0: 12d} ".format(int(i))
            else:
                linestr= linestr+"{0} ".format(i)
        prettyarray.append(linestr)
    return prettyarray
#---------------------------------------------------------------------------------------------#

#---- function arthmetic:---------------------------------------------------------------------#
def arithmetic(val,funct):
    sign = funct.replace('x','')[0]
    if sign == '+':
        return val+float(funct.split(sign)[1])
    if sign == '-':
        return val-float(funct.split(sign)[1])
    if sign == '*':
        return val*float(funct.split(sign)[1])
    if sign == '/':
        return val/float(funct.split(sign)[1])
    if sign == '^':
        return val**float(funct.split(sign)[1])
    else:
        sys.exit('arithmetic function some sort of error')
#----------------------------------------------------------------------------------------------#


#---- function text substitution: ------------------------------------------------------------#
def text_edit(i,oldtext,newtext):
    return i.replace(oldtext,newtext)

#---------------------------------------------------------------------------------------------#

   

(labels,header,data,numtolabel) = read_starfile(sys.argv[1])

print"{0} data columns found".format(len(labels))
labelslist = range(0,len(labels))
for i in labelslist:
    print'{0:>2})  {1}'.format(i,numtolabel[i].replace('_rln',''))

print "\nWhich columns to edit? Enter a list separated by commas IE: 1,2,4,6"
toedit = raw_input('columns: ')

coldellist = []
editsdic = {}
for i in labels:
    if str(labels[i]) in toedit.split(','):
            print "\n** working on column {0}: {1}**".format(labels[i],i)
            print '''type of edit to make:
1) arithmetic
2) edit a text line
3) delete column'''
            choice = raw_input('choice: ')
            if choice == '1':
                print "function to apply, with x for the original value.  IE:  x+2, x-10, or x*5"
                editsdic[i] = ('arithmetic',raw_input('function: '))
            if choice == '2':
                print "example line: "
                print "{0}".format(data[0][labels[i]])
                print "write the piece of text to substitute/delete:"
                textsub = raw_input('text to substitute/delete: ') 
                editsdic[i] = ('text edit',textsub,raw_input('text to replace it with (or leave blank to delete): '))
            if choice == '3':
                editsdic[i] = ('delete column')
                coldellist.append(i)
    else:
        editsdic[i] = ('NOCHANGE')

print "edits to make: "
for i in editsdic:
    if editsdic[i] != 'NOCHANGE':
        print '{0}\t\t{1}'.format(i,editsdic[i])

doit = raw_input("do it (Y/N): ")
if doit not in ('Y','y','yes','YES','Yes'):
    sys.exit('quitting')

lineno = 1
newdata = []
for line in data:
    print 'working on line {0}'.format(lineno)
    n = 0
    newline = []
    for i in line:
        thingtoedit = numtolabel[n]
        print thingtoedit
        print editsdic[thingtoedit]
        if editsdic[thingtoedit][0] == 'arithmetic':
            newline.append(arithmetic(float(i),editsdic[numtolabel[n]][1]))

        elif editsdic[thingtoedit][0] == 'text edit':
            newline.append(text_edit(i,editsdic[numtolabel[n]][1],editsdic[numtolabel[n]][2]))
        
        elif editsdic[thingtoedit] == 'NOCHANGE':
            newline.append(i)
        elif editsdic[thingtoedit] == 'delete column':
            print 'deleted {0}'.format(thingtoedit)
        n+=1
    newdata.append(newline)
    lineno+=1
    
prettydata = make_pretty_numbers(newdata)

output = open('STAR-edit.star','w')

print coldellist
n = 1
if len(coldellist) > 0:
    for i in header:
        if '#' in i:
            if i.split('#')[0] not in coldellist:
                output.write('{0}#{1}\n'.format(i.split('#')[0],n))
                n+=1
        else:
            output.write('{0}\n'.format(i))
for i in prettydata:
    output.write('{0}\n'.format(i))
print "wrote output file STAR-edit.star"
