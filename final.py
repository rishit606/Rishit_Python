from pandas.io.json import json_normalize

import pandas as pd
#Read Start of day file
Input = pd.read_csv('Input_StartOfDay_Positions.txt', sep=",")
#Read transactions file
transactions = pd.read_json('1537277231233_Input_Transactions.txt')
#Group based on Instrument and TransactionType and get the sum of TransactionQuantity. 
agg_trns = transactions.drop('TransactionId', axis = 1).groupby(by = ['Instrument', 'TransactionType'],axis = 0, as_index=False).sum()
#Merge Start of day positions with Transaction and if no transaction for the respective Instrument - replace with 0.
inter = Input.merge(agg_trns, how = 'outer').fillna(0)

#Create a function for the calculation of End of day position.
def calc(row):
    if (row['TransactionType'] == 'B') & (row['AccountType'] == 'E')  : x = 1
    elif (row['TransactionType'] == 'B') & (row['AccountType'] == 'I') : x = -1
    elif (row['TransactionType'] == 'S') & (row['AccountType'] == 'E') : x = -1
    else : x = 1
    
    return x
#Understand how the Delta needs to be calculated for TransactionQuantity- 1 means to add and -1 means to subtract.
inter['mul_factor'] = inter.apply(calc, axis = 1)
inter['Delta'] = inter['TransactionQuantity']*inter['mul_factor']
#Get the total of TransactionQuantity for each instrument and Account Type
final = inter[['Instrument', 'Account', 'AccountType', 'Quantity','Delta']].groupby(['Instrument', 'Account', 'AccountType', 'Quantity'], as_index = False).sum()
#Add the delta with actual Quantity to get the EOD_position
final['Quantity'] = final['Delta'] + final['Quantity']
final.to_csv("EOD_positions.txt",sep=',',index=False)
