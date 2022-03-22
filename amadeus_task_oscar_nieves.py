# -*- coding: utf-8 -*-
"""
Amadeus Job interview task
Author: Oscar A. Nieves
Last updated: March 22 2022

The following is a Python 3 implementation of the algorithm outlined in
the associated PDF file entitled "Amadeus Task - Oscar Nieves"
"""
import copy
import pprint
from sys import exit
pp = pprint.PrettyPrinter(indent=2)

# ---------------- Select case number ---------------------------------------#
# Enter your case number here (1-7, or 100 = oscar's example)
Case_number = 1

# --------------------------- Load data -------------------------------------#
# Define Input DATA from text file
input_file = "test_case_" + str(Case_number) + ".txt"
try:
    file1 = open(input_file, "r")
except:
    print("ERROR: Text file with case number not found in directory...")
Lines = file1.readlines()
ReadLines = []
for line1 in Lines:
    if line1[-1] == "\n":
        splitLine = line1[:-1].split(" ")
    else:
        splitLine = line1.split(" ")
    for n in range(len(splitLine)):
        splitLine[n] = int(splitLine[n])
    ReadLines.append(splitLine)

# ------------------------ Functions ----------------------------------------#
def Transform(InputMachine):
    InputMachine[1] = 0
    OutputMachine = InputMachine
    return OutputMachine

def SkipEmpty(InputList):
    output = []
    for i in range(len(InputList)):
        if output == [] and InputList[i] == []: 
            continue #skip iteration if InputList[i] is empty
        else:
            output.append(InputList[i])
    return output

def CountEmpty(InputList):
    counter = 0
    for i in range(len(InputList)):
        if InputList[i] == []:
            counter += 1
        else:
            break
    return counter

# Calculate list of possible paths between current set and next set
def MergeSpecial(First, Second):
    len_1 = len(First)
    len_2 = len(Second)
    new_item = [[] for i in range(len_1)]
    
    # Duplicate and transform last element of each row in First
    First_copy = copy.deepcopy(First)
    for i in range(len_1):
        list_i = First_copy[i]
        new_item[i] = Transform(list_i[-1])
    
    # Combine in special way
    if Second == []:
        new_copies = copy.deepcopy(First)
        for i in range(len_1):
            new_copies[i].append(new_item[i])
    else:
        copies = [copy.deepcopy(Second) for i in range(len_1)]
        counter_1 = len_2+1
        for i in range(len_1):
            copies[i].insert(0, [new_item[i]])
        
        new_copies = []
        for i in range(len_1):
            for n in range(counter_1):
                new_copies.append(copies[i][n])
                
        # Insert First values at the back of Second
        index0 = 0
        len_first = len(First[0])
        for i in range(len_1):
            for n in range(counter_1):
                for j in range(len_first):
                    new_copies[index0].insert(j, First[i][j])
                index0 += 1

    output = new_copies
    return output
        
# Generate network table of all possible paths
def NetworkTable(InputSetSequence):
    output = []
    len_1 = len(InputSetSequence)
    i = 0
    output = copy.deepcopy(InputSetSequence[i])
    while i < len_1-1:
        list_current = output
        list_next = copy.deepcopy(InputSetSequence[i+1])
        output = MergeSpecial(list_current, list_next)
        i += 1
    return output

# Weights calculator
def w(i=1, j=1, t=1, D_i=1, P_i=1, R_i=1, G_i=1, A_ij=0, L=1):
    if A_ij < 0: 
        return -L # Ran out of money
    else:
        if i == 0 or j == 0: # No machine bought so far
            return 0
        else:
            if i == j and t > D_i: # machine is owned and operating
                return G_i
            elif i == j and t <= D_i: # machine is being bought today
                return -P_i
            elif i != j and P_i == 0: # machine is owned today, sold tomorrow
                return G_i + R_i
            elif i != j and P_i != 0: # machine is bought today, sold tomorrow
                return R_i - P_i

# ------------------------Run program, Processing Inputs---------------------#
inputs = ReadLines[0]
N = inputs[0]
C = inputs[1]
D = inputs[2]

if len(ReadLines) == 1: # if no machine values detected
    print("Case " + str(Case_number) + ": " + str(C))
    exit(0)

M_initial = []
for n in range(1,len(ReadLines)):
    M_initial.append(ReadLines[n])

# Sort array M in ascending order of 1st element of each machine
M = sorted(M_initial, key=lambda x: x[0], reverse=False)

# Break down M into smaller subsets
m_subsets = [[] for i in range(D+1)]
for t in range(1, D+1):
    for i in range(N):
        M_i = M[i]
        D_i = M_i[0]
        if D_i == t:
            M_i.append(i+1) #append machine number at the end
            m_subsets[t-1].append([M_i])
        if t == 1 and i == 0:
            m_subsets[t-1].append([[1,0,0,0,0]]) # no machine at start
        else:
            continue

# Generate Network table
m_input = SkipEmpty(m_subsets)
network = NetworkTable(m_input)
network_size = len(network)
start_index = CountEmpty(m_subsets) 

# Set negative value for implausible edges
G_array = [] 
for i in range(N):
    G_array.append(M[i][-1])
L = D*max(G_array)

# Begin optimization procedure
W = [[0]*D for n in range(network_size)]
A = [[C]*(D+1) for n in range(network_size)] 

for n in range(network_size):
    row = network[n]
    t = start_index
    day = t+1
    for k in range(len(row)-1):
        i = row[k][-1]
        j = row[k+1][-1]
        D_i = row[k][0]
        P_i = row[k][1]
        R_i = row[k][2]
        G_i = row[k][3]
        A_ij = A[n][t]
        w_ij_t = w(i, j, day, D_i, P_i, R_i, G_i, A_ij, L)
        W[n][t] = w_ij_t
        A[n][t+1] = A[n][t] + w_ij_t
        t += 1
        day += 1

# Compute R_final
A_final = [0 for i in range(network_size)]
A_values = copy.deepcopy(A)
for n in range(network_size):
    row = network[n]
    R_prev = row[-1][2]
    A_final[n] = A_values[n][-1] + R_prev

# Find maximum value at t = D+1
A_max = max(A_final)
index_at_max = A_final.index(A_max)

# Display output
print("Case " + str(Case_number) + ": " + str(A_max))