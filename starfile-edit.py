#!/usr/bin/python
# Edit individual columns in a star file 
# Matt Iadanza - 2016- Astbury Centre for Structural Biology, University of Leeds 

import sys
vers = '1.0'

if len(sys.argv) < 2:
    sys.exit('USAGE: star-edit.py <starfile>\nrun with the --headless tag to output without the starfile header')

headless = False
if '--headless' in sys.argv:
    headless = True



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
    if sign == 'I':
        return (-1*val*float(funct.split(sign)[1]))
    else:
        sys.exit('arithmetic function some sort of error')
#----------------------------------------------------------------------------------------------#


#---- function text substitution: ------------------------------------------------------------#
def text_edit(i,oldtext,newtext):
    return i.replace(oldtext,newtext)

#---------------------------------------------------------------------------------------------#

   
# get the headers, labels, and data

(labels,header,data,numtolabel) = read_starfile(sys.argv[1])
print '** Easy star file editor vers {0} **'.format(vers)
print"{0} data columns found".format(len(labels))
labelslist = range(0,len(labels))
for i in labelslist:
    print'{0:>2})  {1}'.format(i,numtolabel[i].replace('_rln',''))

print "\nWhich columns to edit? Enter a list separated by commas IE: 1,2,4,6"
toedit = raw_input('columns: ')

# error checks
colerrcheck = toedit.split(',')
if len(toedit) == 0:
    sys.exit('quitting')
for i in colerrcheck:
    if is_number(i) == False:
        sys.exit('ERROR: Oops! {0} is not a valid column'.format(i))
    if int(i) > len(labelslist):
        sys.exit('ERROR: Oops! there is no colum {0}'.format(i))

# ask what to do with them

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
            if choice not in ('1','2','3'):
                sys.exit('ERROR: Not a valid choice...')
            if choice == '1':
                print "\nExample value: "
                print "{0}".format(data[0][labels[i]])
                print "function to apply, with x for the original value.  IE:  x+2, x-10, x/4, x*5, or x^2.  \nUse I to multiply by a negative number IE xI1 = x*(-1)"
                funct = raw_input('function: ')   
                
                #error checks
                if is_number(data[0][labels[i]]) == False:
                    sys.exit("ERROR: This column doesn't contain a number")
                if funct[0] != 'x' or funct[1] not in ('=','-','/','*','^','+','I') or len(funct) < 3:
                    sys.exit('ERROR: must be in the form of x<sign><number>')
                try:
                    testval = funct[2:]
                    testval = float(testval)
                except ValueError:
                    sys.exit('ERROR: x{0}{1} not vaild function'.format(funct[1]),testval)
                
                editsdic[i] = ('arithmetic',funct)
            
            if choice == '2':
                print "\nExample value: "
                print "{0}".format(data[0][labels[i]])
                print "write the piece of text to substitute/delete:"
                textsub = raw_input('text to substitute/delete: ')
                
                # error checks 
                if ' ' in textsub:
                    sys.exit('ERROR: "{0}" no spaces allowed!'.format(textsub))
                subtext = raw_input('text to replace it with (or leave blank to delete): ')
                if ' ' in subtext:
                    sys.exit('ERROR: "{0}" no spaces allowed!'.format(subtext))
                
                editsdic[i] = ('text edit',textsub,subtext)
            
            if choice == '3':
                editsdic[i] = ('delete column')
                coldellist.append(i)
    else:
        editsdic[i] = ('NOCHANGE')

# confirm with the user

print "edits to make: "
for i in editsdic:
    if editsdic[i] != 'NOCHANGE':
        print '{0}\t\t{1}'.format(i,editsdic[i])

doit = raw_input("do it (Y/N): ")
if doit not in ('Y','y','yes','YES','Yes'):
    sys.exit('quitting')

# DO IT!

newdata = []
counter = 0
for line in data:
    n = 0
    newline = []
    counter +=1
    for i in line:
        thingtoedit = numtolabel[n]        
        if editsdic[thingtoedit][0] == 'arithmetic':
            newline.append(arithmetic(float(i),editsdic[numtolabel[n]][1]))
            
        elif editsdic[thingtoedit][0] == 'text edit':
            newline.append(text_edit(i,editsdic[numtolabel[n]][1],editsdic[numtolabel[n]][2]))
        
        elif editsdic[thingtoedit] == 'NOCHANGE':
            newline.append(i)
        n+=1
    newdata.append(newline)
    if counter == 1000:
        sys.stdout.write('.')
        sys.stdout.flush()
        counter = 0
 
# Write the starfile
print "writing output file"
prettydata = make_pretty_numbers(newdata)
output = open('STAR-edit.star','w')

#write the header if desired
if headless == False:
    n = 1
    if len(coldellist) > 0:
        for i in header:
            if '#' in i:
                if i.split('#')[0] not in coldellist:
                    output.write('{0}#{1}\n'.format(i.split('#')[0],n))
                    n+=1
            else:
                output.write('{0}\n'.format(i))

# write the data

for i in prettydata:
    output.write('{0}\n'.format(i))
print "\nwrote output file: STAR-edit.star"
