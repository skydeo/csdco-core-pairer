import csv, copy, timeit
startTime = timeit.default_timer()

debug = 0

#### Settings

# maxL = Maximum length (in meters) of core material wanted in a D-Tube

# mcpt = Maximum cores per tube (regardless of maximum length)

# mcsd = Maximum core search depth
#		Maximum # of rows down-list to look in order to find a core that fits

maxL = 1.5
mcpt = 8
mcsd = 8

mcptRange = 2
mcsdRange = 2

#### End of user-defined settings.

# Create some empty arrays
mcpts = []
mcsds = []
valueRanges = []
cList = []
runs = []

# Import the core list, right now it must be in same folder and named 'coreList.csv'
with open('coreList.csv', 'r') as inputFile:
	fileReader = csv.reader(inputFile, delimiter='\n')
	for row in fileReader:
		cList.append(row[0].split(','))

# Remove BOM if it's there
if '\ufeff' in cList[0][0]:
	cList[0][0] = cList[0][0].replace('\ufeff','')
	if debug:
		print('BOM removed.')

# Add index to coreList. Needed to know how far to search for partner core.
for i in range(0,len(cList)):
	cList[i].append(i)

for r in range(-mcptRange,mcptRange+1):
	mcpts.append(r+mcpt)

for r in range(-mcsdRange,mcsdRange+1):
	mcsds.append(r+mcsd)

valueRanges = [(x, y) for x in mcpts for y in mcsds]


def pair(coreList, mcpt, mcsd):
	# Set up some emcpty variables
	dNum = 0
	pairings = [[]]
	lengths = [float(0)]

	# Create a true copy of the coreList object, which will be used as a stack
	coreStack = copy.deepcopy(coreList)

	# Pair
	while (len(coreStack) > 0):
		cCore = coreStack.pop(0);

		if debug:
			print('\ncCore: ',cCore,)

		pairings[dNum].append(cCore[0])
		lengths[dNum] += float(cCore[1])

		searchSet = []

		i = 0
		while (i < len(coreStack)):
			if (coreStack[i][2] <= (cCore[2] + mcsd)):
				sCore = coreStack[i]
				searchSet.append(sCore)
			i += 1

		if debug & (len(searchSet) > 0):
			print('searchSet: ',searchSet)

		fitSet = []

		for sCore in searchSet:
			if (lengths[dNum] + float(sCore[1]) <= maxL) & (len(pairings[dNum]) < mcpt):
				lengths[dNum] += float(sCore[1])
				pairings[dNum].append(sCore[0])
				fitSet.append(sCore)

		if debug & (len(fitSet) > 0):
			print('fitSet:',fitSet)

		for fCore in fitSet:
			coreStack.pop(coreStack.index(fCore))

		if len(coreStack) > 0:
			dNum += 1
			pairings.append([])
			lengths.append(float(0))

	# Append lengths back on to end of pairing list.
	for r in range(0,len(pairings)):
		pairings[r] += [''] * (mcpt - len(pairings[r]))
		pairings[r].append(str(round(lengths[r],3)))

	return pairings

# Run through all mcpts
for valueSet in valueRanges:
	pairings = pair(cList, valueSet[0], valueSet[1])
	runs.append((valueSet[0],valueSet[1],len(pairings)))
	# if debug:
	print('{0} D-Tubes used (per half) with {1} cores per tube and a search depth of {2}.'.format(len(pairings),valueSet[0],valueSet[1]))

# Sort runs by D-Tube usage
runs.sort(key=lambda tup: tup[2])

print('\nMinimum D-Tube usage ({0}, per half) found using {1} cores per tube and a search depth of {2}.\n'.format(runs[0][2],runs[0][0],runs[0][1]))

if (len(runs) > 1):
	# Run minimum valueSet again for export
	pairings = pair(cList,runs[0][0],runs[0][1])

# Append '-W' once, write those, replace it with '-A', write that.
with open('pairedDTubes.csv', 'w') as saveFile:
	filewriter = csv.writer(saveFile)
	for row in pairings:
		for el in range(0,len(row)-1):
			if row[el] != '':
				row[el] += '-W'
		filewriter.writerow(row)
	for row in pairings:
		for el in range(0,len(row)-1):
			if row[el] != '':
				row[el] = row[el][:-2] + '-A'
		filewriter.writerow(row)

endTime = timeit.default_timer()

print('{0} total cores paired into {1} total D-Tubes.\n'.format(str(len(cList)*2),str(len(pairings)*2)))
print('Completed in {0} seconds.'.format(round((endTime - startTime),3)))
