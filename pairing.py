import csv
import copy
import timeit
import argparse

def pair_cores(input_filename, **kwargs):
  debug = False

  max_core_length = 1.5 if kwargs['max_core_length'] is None else kwargs['max_core_length']
  max_num_cores = 8 if kwargs['max_num_cores'] is None else kwargs['max_num_cores']
  max_search_depth = 6 if kwargs['max_search_depth'] is None else kwargs['max_search_depth']
  run_variation = 2 if kwargs['run_variation'] is None else kwargs['run_variation']

  # if output_filename in kwargs:
  #   output_filename = kwargs['output_filename']
  # else:
  output_filename = ''.join(input_filename.split('.')[:-1]) + '_paired.csv' 

  
  # Create some empty arrays
  mcpts = []
  mcsds = []
  valueRanges = []
  cList = []
  runs = []

  # Import the core list, right now it must be in same folder and named 'coreList.csv'
  with open(input_filename, 'r', encoding='utf-8-sig') as f:
    csv_reader = csv.reader(f, delimiter='\n')
    for row in csv_reader:
      cList.append(row[0].split(','))

  # Add index to coreList. Needed to know how far to search for partner core.
  for i in range(0,len(cList)):
    cList[i].append(i)

  for r in range(-1*run_variation,run_variation+1):
    mcpts.append(r+max_num_cores)

  for r in range(-run_variation,run_variation+1):
    mcsds.append(r+max_search_depth)

  valueRanges = [(x, y) for x in mcpts for y in mcsds]


  def pair(core_list, max_num_cores, max_search_depth):
    # Set up some empty variables
    dNum = 0
    pairings = [[]]
    lengths = [float(0)]

    # Create a true copy of the core_list object, which will be used as a stack
    coreStack = copy.deepcopy(core_list)

    # Pair
    while coreStack:
      cCore = coreStack.pop(0);

      if debug:
        print('\ncCore: ',cCore,)

      pairings[dNum].append(cCore[0])
      lengths[dNum] += float(cCore[1])

      searchSet = []

      i = 0
      while (i < len(coreStack)):
        if (coreStack[i][2] <= (cCore[2] + max_search_depth)):
          sCore = coreStack[i]
          searchSet.append(sCore)
        i += 1

      if debug & (len(searchSet) > 0):
        print('searchSet: ',searchSet)

      fitSet = []

      for sCore in searchSet:
        if (lengths[dNum] + float(sCore[1]) <= max_core_length) & (len(pairings[dNum]) < max_num_cores):
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
      pairings[r] += [''] * (max_num_cores - len(pairings[r]))
      pairings[r].append(str(round(lengths[r],3)))

    return pairings

  # Run through all mcpts
  for valueSet in valueRanges:
    pairings = pair(cList, valueSet[0], valueSet[1])
    runs.append((valueSet[0],valueSet[1],len(pairings)))
    # if debug:
    print(f'{len(pairings)} D-Tubes used (per half) with {valueSet[0]} cores per tube and a search depth of {valueSet[1]}.')

  # Sort runs by D-Tube usage
  runs.sort(key=lambda tup: tup[2])

  print(f'\nMinimum D-Tube usage ({runs[0][2]}, per half) found using {runs[0][0]} cores per tube and a search depth of {runs[0][1]}.\n')

  if (len(runs) > 1):
    # Run minimum valueSet again for export
    pairings = pair(cList,runs[0][0],runs[0][1])

  # Append '-W' once, write those, replace it with '-A', write that.
  with open(output_filename, 'w', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f)
    for row in pairings:
      for el in range(0,len(row)-1):
        if row[el] != '':
          row[el] += '-W'
      csv_writer.writerow(row)
    for row in pairings:
      for el in range(0,len(row)-1):
        if row[el] != '':
          row[el] = row[el][:-2] + '-A'
      csv_writer.writerow(row)


  print(f'{str(len(cList)*2)} total cores paired into {str(len(pairings)*2)} total D-Tubes.\n')


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Automatically pair cores into the minimum number of D-tubes possible.')
  parser.add_argument('core_list', type=str, help='Name of core list csv file.')
  parser.add_argument('-o', '--output-filename', type=str, help='Filename for export.')
  parser.add_argument('-ml', '--max-core-length', type=float, help='Maximum length of core material to fit in one D-tube.')
  parser.add_argument('-msd', '--max-search-depth', type=int, help='Maximum distance down-list to search for a core that fits.')
  parser.add_argument('-mc', '--max-num-cores', type=int, help='Maximum number of cores to fit in one D-tube.')
  parser.add_argument('-rv', '--run-variation', type=int, help='Integer to vary --max-search-depth and --max-num-cores by.')
  args = parser.parse_args()

  start_time = timeit.default_timer()
  pair_cores(args.core_list, **vars(args))
  print(f'Completed in {round((timeit.default_timer() - start_time),2)} seconds.')

