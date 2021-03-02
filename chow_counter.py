#Import packages
import re
import tkinter as tk
import time
import math
from unicodedata import numeric
import matplotlib.pyplot as plt
import numpy as np
import mysql.connector
from mysql.connector import Error
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from selenium import webdriver
import os

def set_dir():
    """sets the working directory to wherever this file is"""
    abspath = os.path.abspath('chow_counter.py')
    dname = os.path.dirname(abspath)
    os.chdir(dname)

def create_server_connection(host_name, user_name, user_password):
    """Creates and returns the connection to the SQL server"""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password)
    except Error as err:
        print(f"Error: '{err}'")
    return connection

def query_all(connection, query):
    """Returns all results from the given SQL quary"""
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        output = cursor.fetchall()
    except Error as e:
        print(f"The error '{e}' occurred")
        output = None
    return output

def read_file(directory):
    """Read txt files and returns each new line as an element in list"""
    with open(directory) as f:
        output = f.read().splitlines()
        f.close()
    return output

def scrape_url(url):
    """Scrapes given url, returns content as string"""
    driver = webdriver.Chrome()
    driver.get(url)
    driver.execute_script(r'''window.scrollTo(0, document.body.scrollHeight);
                          lenOfPage=document.body.scrollHeight;
                          return lenOfPage;''')
    time.sleep(5)
    string = driver.page_source
    driver.quit()
    return string

###List manipulations
def add_lists(list1, list2):
    """Adds two lists together element-wise"""
    output = []
    for i, element in enumerate(list1):
        temp = float(element) + float(list2[i])
        output.append(temp)
    return output

def list_split(input_list, delim):
    """Seperates each element in a list by given delimitor"""
    new_list = []
    [new_list.append(element.split(delim)) for element in input_list]
    return new_list

def pull_element(input_list, index):
    """Takes a list of lists. Returns a list of all the elements at given index"""
    output_list = []
    for i, element in enumerate(input_list):
        output_list.append(element[index])
    return output_list

def searchlist(list1, list2):
    """Removes all elements in list1 that are in list2 and returns them"""
    list3 = [None]*len(list1)
    for i, element in enumerate(list1):
        temp1 = []
        temp2 = []
        for element in list1[i]:
            if element.lower() not in list2:
                temp1.append(element)
            else:
                temp2.append(element)
            list1[i] = temp1
            list3[i] = temp2
    return list3

def check_overlap(input_list, input_dictionary, **kwargs):
    """Checks for overlapping elements in given lists. If exclusive, returns True when no overlap"""
    dictionary = {'exclusive':False}
    dictionary.update(kwargs)
    test = 0
    for element in input_list:
        if str(element) in input_dictionary:
            test = test + 1
    if not dictionary['exclusive'] and test == len(input_list):
        return True
    elif dictionary['exclusive'] and test == 0:
        return True
    else:
        return False

def pattern_replace(input_list, old_pattern, new_pattern):
    """Replaces patterns in a list of strings with the new pattern and returns new string"""
    output_list = [None]*len(input_list)
    for i, element in enumerate(input_list):
        output_list[i] = re.sub(old_pattern, new_pattern, element)
    return output_list

def find_permutations(input_list, join_string):
    """Returns list of possible combinations of new strings given a list of strings"""
    output_list = []
    for j in range(0, len(input_list)):
        for k in range(j+1, len(input_list)+1):
            output_list.append(join_string.join(input_list[j:k]))
    output_list.sort(key=len, reverse=True)
    return output_list

############### Dictionary Stuff
#Searches a dictionary for each element in a string. Returns the value.
def search_dict(input_list, input_dictionary, empty, **kwargs):
    """Searches a dictionary for elements in given string. Returns the first key found.

    **kwargs
    ----------
    plural: If true, will attempt to find value of element with the last 1 or 2 characters removed
    fail: If true, will generate error if no matches found
    key: If true, returns the key as well as the value
    index: If true, returns the index of the element matched in list

    """
    dictionary = {'plural':False, 'fail':False, 'key':False, 'index':False}
    dictionary.update(kwargs)
    for element in input_list:
        if element in input_dictionary:
            output = [input_dictionary[element]]
            key = element
            index = input_list.index(element)
            break
        elif dictionary['plural'] and element[:-1] in input_dictionary:
            output = [input_dictionary[element[:-1]]]
            key = element[:-1]
            index = input_list.index(element)
            break
        elif dictionary['plural'] and element[:-2] in input_dictionary:
            output = [input_dictionary[element[:-2]]]
            key = element[:-2]
            index = input_list.index(element)
            break
        else:
            pass
    if dictionary['key']:
        output.append(key)
    if dictionary['index']:
        output.append(index)
    if not dictionary['fail'] and "output" not in locals():
        output = empty
    return output

def search_dict_simple(input_list, input_dictionary):
    """Searches a dictionary for a list of keys. Returns the values."""
    output_list = []
    for element in input_list:
        output_list.append(input_dictionary[element])
    return output_list

def create_dict(keys, values):
    """Creates a dictionary given a list of keys and values"""
    dictionary = {}
    for i, element in enumerate(values):
        dictionary.update({keys[i]:element})
    return dictionary


def eval_complex(string, **kwargs):
    """"Attempts to convert a string to a float. If failarg is true, returns None when failed."""
    dictionary = {'failarg': False}
    dictionary.update(kwargs)
    for i in range(0, 1):
        try:
            output = float(eval(str(string)))
            break
        except:
            pass
        try:
            output = float(numeric(str(string)))
            break
        except:
            if dictionary['failarg']:
                output = None
            else:
                break
    return output

def eval_complex_list(input_list):
    """Returns the sum of all elements in list. Ignores non-floatables"""
    output = 0
    for i, element in enumerate(input_list):
        try:
            output = output + float(eval(str(element)))
            continue
        except:
            pass
        try:
            output = output + float(numeric(str(element)))
            continue
        except:
            continue
    return output

################## Seb Scraping and SQL Section ##########################
set_dir()

#Opens window for user input, saves input as url.
url_root = tk.Tk()
url_var = tk.StringVar()
url_text = tk.Label(master=url_root, text="Enter your AllRecipes URL here:")
url_entry = tk.Entry(master=url_root, textvariable=url_var)
url_button = tk.Button(master=url_root, text="Go", command=url_root.destroy)

url_text.pack()
url_entry.pack()
url_button.pack()

url_root.mainloop()
url = url_var.get()

#Get the source code for the provided URL.
content = scrape_url(url)

#Save the ingredients list as ingredients_raw.
#Depending on the recipe, Allrecipes will have one of two possible styles of source code.
#So we have a list of two possible patterns.
ingredients_pattern = ["<span class=\"recipe-ingred_txt added\" data-id=\"0\""
                       +" data-nameid=\"0\" itemprop=\"recipeIngredient\">(.*?)</span>"]
ingredients_pattern.append('''"ingredients-item-name">. *(.*?). *<''')

if content[16:21] == 'class':
    INDEX = 1
else:
    INDEX = 0

ingredients_raw = re.findall(ingredients_pattern[INDEX], content, flags=re.DOTALL)

#Create the connection to our SQL server.
END_POINT = 'chowcounter-databases.czaa9pf5cvrz.us-east-2.rds.amazonaws.com'
SQL_USERNAME = 'admin'
SQL_PASSWORD = 'LlamaPants162'
cnx = create_server_connection(END_POINT, SQL_USERNAME, SQL_PASSWORD)

#Pull all names from the database and their USDA ID from the food name table.
CMD = '''SELECT ingred_names, usda_id
         FROM scehma1.ingredient_names;'''
database = query_all(cnx, CMD)
ingredient_DB = create_dict(pull_element(database, 0), pull_element(database, 1))

#Load up some refrence lists for stop words and units.
stop_words = read_file(r'txt_files\stop_words.txt')
units = read_file(r'txt_files\units.txt')

#Do some formatting for the units. We want refrence units, standard units,
#and the factor to be three seperate lists. Make a dictionary as well.
units = list_split(units, ',')
unit_refrence = pull_element(units, 0)
unit_stanard = pull_element(units, 1)
unit_factor = pull_element(units, 2)

unit_dict = {}
for i, element in enumerate(unit_refrence):
    temp = {element: [unit_stanard[i], unit_factor[i]]}
    unit_dict.update(temp)

#Clean the raw ingredients.
for i, element in enumerate(ingredients_raw):
    ingredients_raw[i] = element.lower()
ingredients = pattern_replace(ingredients_raw, ",", '')
ingredients = pattern_replace(ingredients, "\u2009", ' ')
ingredients = list_split(ingredients, ' ')
searchlist(ingredients, stop_words)

#Preallocate key variables for each ingredient.
units = [None] * len(ingredients)
amounts = [None] * len(ingredients)
usda_id = [None] * len(ingredients)
ingred_names = [None] * len(ingredients)

###### NLP Section #######################################################
root = tk.Tk()
for i, line in enumerate(ingredients):
#Pass 1 Format: 1 (14 oz) can of corn
#[amount of packages] ([size of package] [unit of package]) [package]...
    try:
        temp = ' '.join(line)
        if '(' not in temp:
            eval('a')
        sub_statement = re.findall(r"\((.*?)\)", temp, flags=re.DOTALL)
        temp = re.sub(r"\((.*?)\) ", '', temp)
        sub_statement = re.sub(r"-", ' ', sub_statement[0])
        temp = list_split([temp], ' ')
        temp = temp[0]
        sub_statement = list_split([sub_statement], ' ')
        sub_statement = sub_statement[0]
        amount1 = eval_complex_list(temp)
        amount2 = eval_complex_list(sub_statement)
        if amount1 == 0 :
            eval('a')
        elif amount2 == 0:
            eval('a')
        try:
            units[i] = unit_dict[sub_statement[-1]][0]
            amounts[i] = (amount1 * amount2 *
                   float(unit_dict[sub_statement[-1]][1]))
        except:
            units[i] = unit_dict[temp[1]][0]
            amounts[i] = amount1 * amount2 * float(unit_dict[temp[1]][1])
        ingredient_phrases = find_permutations(line[2:], ' ')
        temp = search_dict(ingredient_phrases, ingredient_DB, None,
                           plural=True, key=True)
        usda_id[i] = temp[0]
        ingred_names[i] = temp[1]
        cmd = '''SELECT food_name
                 FROM scehma1.nutrition_data
                 WHERE usda_id = \''''+usda_id[i]+'\';'
        name = query_all(cnx, cmd)
        label = tk.Label(master=root, text=('Identified \"'
                                            +str(ingredients_raw[i])+'\" as \"'
                                            +name[0][0]+'\"'))
        label.pack()
        continue
    except:
        pass

#Check 2 Format: 1 potato
#[amount] [amount less than 1 (optional)] [ingredient phrases]...
    try:
        if not check_overlap(line, unit_dict, exclusive=True):
            eval('a')
        units[i] = 'count'
        ingredient_phrases = find_permutations(line, ' ')
        temp = search_dict(ingredient_phrases, ingredient_DB, None, plural=True, key=True)
        usda_id[i] = temp[0]
        ingred_names[i] = temp[1]
        try:
            amounts[i] = int(line[0]) + eval_complex(line[1])
        except:
            amounts[i] = eval_complex(line[0])
        if amounts[i] > eval_complex(line[0]) + 1:
            eval('a')
        cmd = 'SELECT food_name \
               FROM scehma1.nutrition_data \
               WHERE usda_id = \''+usda_id[i]+'\';'
        name = query_all(cnx, cmd)
        label = tk.Label(master=root, text=('Identified \"'
                                            +str(ingredients_raw[i])+'\" as \"'
                                            +name[0][0]+'\"'))
        label.pack()
        continue
    except:
        pass

#Check 3 Format: 1 pound potatoes.
#[amount] [unit] [ingredient phrases 1] [ingredient phrases 2] ...
    try:
        temp = search_dict(line, unit_dict, None, key=True, index=True)
        units[i] = temp[0][0]
        amounts[i] = eval_complex_list(line[0:temp[2]])
        amounts[i] = amounts[i] * float(temp[0][1])
        ingredient_phrases = find_permutations(line[temp[2]+1:], ' ')
        temp = search_dict(ingredient_phrases, ingredient_DB, None, plural=True, key=True)
        usda_id[i] = temp[0]
        ingred_names[i] = temp[1]
        cmd = '''SELECT food_name
                 FROM scehma1.nutrition_data
                 WHERE usda_id = \''''+usda_id[i]+"\';"
        name = query_all(cnx, cmd)
        label = tk.Label(master=root, text=('Identified \"'
                                            +str(ingredients_raw[i])+'\" as \"'
                                            +name[0][0]+'\"'))
        label.pack()
        continue
    except:
        pass

#Pass 4: If there are no units or amounts, it's not something that can be quantified.
#Most likely a phrase like "salt and pepper to taste".
#Say the amount is 0, making the units and ingredient arbitray.
    try:
        temp = search_dict(unit_dict, line, None, single=True)
        for element in line:
            temp += [eval_complex(element, failarg=True)]
        temp = list(filter(None, temp))
        if temp != []:
            eval('a')
        amounts[i] = 0
        usda_id[i] = '0'
        label = tk.Label(master=root, text=('\"'+str(ingredients_raw[i])
                                            +"\" cannot be processed without a defined amount"
                                            +". Will be ignored for analysis."))
        label.pack()
        continue
    except:
        label = tk.Label(master=root, text=('\"'+str(ingredients_raw[i])
                                            +"\" cannot be identified."
                                            +" Will be ignored for analysis."))
        label.pack()
        amounts[i] = 0
        usda_id[i] = '0'
        continue

processing_button = tk.Button(master=root, text="OK", command=root.destroy)
processing_button.pack()
root.mainloop()


######## Nutrition Processing Section################
#All nutritional data is per 100 grams. Amounts need to be converted to 100 gram units.
for i, element in enumerate(units):
    if usda_id[i] == '0':
        continue
    elif element == "count":
        cmd = '''SELECT count_density
                 FROM scehma1.ingredient_names
                 WHERE ingred_names = \''''+ingred_names[i]+'\';'
        temp = query_all(cnx, cmd)
        amounts[i] = amounts[i]*float(temp[0][0])
    elif element == 'cup':
        cmd = '''SELECT density
                 FROM scehma1.ingredient_names
                 WHERE ingred_names = \''''+ingred_names[i]+'\';'
        temp = query_all(cnx, cmd)
        amounts[i] = amounts[i]*float(temp[0][0])
    elif element == 'gram':
        amounts[i] = amounts[i]/100

#Remove the nutrtionally nulls ingredients, marked as having a USDA ID of 0.
for i, element in reversed(list(enumerate(usda_id))):
    if element == '0':
        usda_id.pop(i)
        amounts.pop(i)
        units.pop(i)

#Sum up the nutrients for each ingredient. Save it in a dictionary along with
#the nutrient name and RDI.
nutrient_names = read_file(r'txt_files\nutrient_names.txt')
nutrient_values = [0] * len(nutrient_names)
nutrient_dict_individul = []
for i, element in enumerate(usda_id):
    cmd = 'SELECT * FROM scehma1.nutrition_data WHERE usda_id = \''+element+'\';'
    temp = query_all(cnx, cmd)
    temp = temp[0]
    temp = list(temp)
    temp = temp[2:]
    temp = [amounts[i]*x for x in temp]
    nutrient_values = add_lists(nutrient_values, temp)
    nutrient_dict_individul.append([ingred_names[i], temp])

nutrient_dict = create_dict(nutrient_names, nutrient_values)

#Calories are reported in joules. Change it to calories 'cause 'Merica.
temp = nutrient_dict['Calories']*0.239
nutrient_dict.update({'Calories':temp})

#Suggest number of servings based on how many calories there are.
calories_total = nutrient_dict['Calories']
servings = math.ceil(calories_total/500)
calories_per_serving = calories_total/servings


#Macronutrients (macro_nuts) piechart, find the total protein, fat, and carbs
#and the calories from eacch.
macro_nut_labels = ['Protein', 'Fats', 'Carbohydrates']
macro_nut_values = [nutrient_dict['Protein']*4, nutrient_dict['Fat']*9,
                    nutrient_dict['Carbohydrates']*4]
macro_nut_fig, macro_nut = plt.subplots()
macro_nut.pie(macro_nut_values, labels=macro_nut_labels, autopct='%1.1f%%')

#Amino Acid score
amino_names = ['Tryptophan',
            'Threonine',
            'Isoleucine',
            'Leucine',
            'Lysine',
            'Methionine',
            'Cystine',
            'Phenylalanine',
            'Tyrosine',
            'Valine',
            'Histidine']

amino_ideal = [7, 27, 25, 55, 51, 25, 0, 47, 0, 32, 18]
amino_values = search_dict_simple(amino_names, nutrient_dict)
amino_values[5] = amino_values[5]+ amino_values[6]
amino_values[6] = 0
amino_values[7] = amino_values[7]+ amino_values[8]
amino_values[8] = 0

amino_diff = [None] * len(amino_values)
for i, element in enumerate(amino_values):
    amino_values[i] = amino_values[i]*1000/nutrient_dict['Protein']
    amino_diff[i] = amino_values[i] - amino_ideal[i]

if min(amino_diff) == 0:
    AMINO_SCORE = 1
else:
    temp = amino_diff.index(min(amino_diff))
    AMINO_SCORE = amino_values[temp]/amino_ideal[temp]

amino_values.pop(8)
amino_values.pop(6)
amino_ideal.pop(8)
amino_ideal.pop(6)


amino_labels = ['Trp',
             'Thr',
             'Ile',
             'Leu',
             'Lys',
             'M+C',
             'W+F',
             'Val',
             'His']

temp = np.arange(len(amino_labels))
amino_fig = plt.figure()
amino_ax = amino_fig.add_subplot(111)
amino_ax.bar(temp, amino_values, color='b', width=0.3)
amino_ax.bar(temp+0.3, amino_ideal, color='g', width=0.3)
amino_ax.bar(amino_labels, [0]*len(amino_labels))
amino_ax.set_ylabel('mg amino acid per g protein')
amino_ax.set_xticks(amino_labels)
amino_ax.set_title('Amino Acid Score: '+str(round(AMINO_SCORE, 2)))
amino_ax.legend(labels=['Values', 'Ideal'])


#Fats
fats_labels = ['Saturated Fats', 'Monounsaturated Fats', 'Polyunsaturated Fats']
fats_values = [nutrient_dict['Saturated Fatty acids'],
               nutrient_dict['Monounsaturated Fatty acids'],
               nutrient_dict['Polyunsaturated Fatty acids']]
fats_fig, fats = plt.subplots()
fats.pie(fats_values, labels=fats_labels, autopct='%1.1f%%')
epa_dha = (nutrient_dict['Omega 3 Fatty Acids, DHA']/servings
           + nutrient_dict['Omega 3 Fatty Acids, EPA']/servings)
omega_3 = epa_dha + nutrient_dict['Omega 3 Fatty Acids, ALA']/servings

#Minerals
mineral_percent = []
mineral_label = ['Ca', 'Fe', 'Mg', 'P', 'K', 'Zn', 'Cu', 'Mn', 'Se']
mineral_keys = ['Calcium', 'Iron', 'Magnesium', 'Phosphorus', 'Potassium',
                'Zinc', 'Copper', 'Manganese', 'Selenium']
mineral_rdi = [1000, 18, 350, 700, 3300, 11, 0.9, 2.3, 55]
for i, element in enumerate(mineral_keys):
    mineral_percent.append(nutrient_dict[element]*100/(float(mineral_rdi[i])*servings))
mineral_fig = plt.Figure()
mineral_ax = mineral_fig.add_subplot(111)
mineral_ax.bar(mineral_label, mineral_percent)
mineral_ax.set_ylabel('Percent of RDI')
mineral_ax.set_title('Minerals per Serving')

#Vitamins
vitamin_percent = []
vitamin_label = ['C', 'B1', 'B2', 'B3', 'B5', 'B6', 'B9', 'B12', 'A', 'E', 'D', 'K', 'Choline']
vitamin_keys = ['Vitamin C', 'Thiamin', 'Riboflavin', 'Niacin', 'Pantothenic acid',
                'Vitamin B6', 'Folate', 'Vitamin B-12', 'Vitamin A, RAE',
                'Vitamin E', 'Vitamin D', 'Vitamin K', 'Choline']
vitimin_rdi = [90, 1.4, 1.6, 18, 6, 2, 400, 6, 600, 10, 5, 80, 550]
for i, element in enumerate(vitamin_keys):
    vitamin_percent.append(nutrient_dict[element]*100/(float(float(vitimin_rdi[i])*servings)))
vitamin_fig = plt.figure()
vitamin_ax = vitamin_fig.add_subplot(111)
vitamin_ax.bar(vitamin_label, vitamin_percent)
vitamin_ax.set_ylabel('Percent of RDI')
vitamin_ax.set_title('Vitamins per Serving')

#Other stuff
table_data = [
    [str(round(nutrient_dict['Calories']/(servings)))+' calories', 'About 500 calories'],
    [str(round(nutrient_dict['Carbohydrates']/servings))+' grams', '56 to 81 grams'],
    [str(round(nutrient_dict['Sugars']/servings))+' grams', 'Less than 7.5 grams'],
    [str(round(nutrient_dict['Fat']/servings))+' grams', '11 to 20 grams'],
    [str(round(nutrient_dict['Protein']/servings))+' grams', 'At least 12.5 grams'],
    [str(round(nutrient_dict['Fiber']/servings, 1))+' grams', 'At least 6.3 grams'],
    [str(round(nutrient_dict['Sodium']/servings, 1))+' mg', 'Less than 575 mg'],
    [str(round(nutrient_dict['Cholesterol']/servings))+' grams', 'Less than 75 mg'],
    [str(round(nutrient_dict['Saturated Fatty acids']/servings, 2))+' grams',
                                                         'Less than 5.5 grams'],
    [str(round(nutrient_dict['Trans Fat']/servings, 3))+' grams', 'Less than 0.5 grams'],
    [str(round(omega_3, 3)*1000)+' mg', 'At least 275 mg'],
    [str(round(epa_dha, 3)*1000)+' mg', 'At least 125 mg']
]

table_collabels = ['Per serving', 'Calorie-adjusted RDV']
table_rowlabels = ['Calories', 'Carbs', 'Sugars', 'Fat', 'Protein', 'Fiber',
                   'Sodium', 'Cholesterol', 'Saturated Fats', 'Trans Fats',
                   'Total Omega 3s', 'EPA+DHA']
table_fig = plt.figure()
table_ax = table_fig.add_subplot(111)
cell_colours = [['#808080', '#808080'],
                ['w', 'w'],
                ['#808080', '#808080'],
                ['w', 'w'],
                ['#808080', '#808080'],
                ['w', 'w'],
                ['#808080', '#808080'],
                ['w', 'w'],
                ['#808080', '#808080'],
                ['w', 'w'],
                ['#808080', '#808080'],
                ['w', 'w']]
table_ax.table(cellText=table_data, rowLabels=table_rowlabels, colLabels=table_collabels,
               cellLoc="center", loc="center", colWidths=[.4, .4, .4],
               rowColours=['#808080', 'w', '#808080', 'w', '#808080', 'w',
                           '#808080', 'w', '#808080', 'w', '#808080', 'w'],
                           cellColours=cell_colours)
table_ax.axis("off")
table_ax.set_title('Recipe makes '+str(servings)+' servings')

#Put all the plots in a window
root = tk.Tk()

table_tk = FigureCanvasTkAgg(table_fig, root)
table_tk.get_tk_widget().grid(column=0, row=0)

aa_tk = FigureCanvasTkAgg(amino_fig, root)
aa_tk.get_tk_widget().grid(column=0, row=1)

macro_tk = FigureCanvasTkAgg(macro_nut_fig, root)
macro_tk.get_tk_widget().grid(column=1, row=0)

fats_tk = FigureCanvasTkAgg(fats_fig, root)
fats_tk.get_tk_widget().grid(column=1, row=1)

vitamin_tk = FigureCanvasTkAgg(vitamin_fig, root)
vitamin_tk.get_tk_widget().grid(column=2, row=0)

mineral_tk = FigureCanvasTkAgg(mineral_fig, root)
mineral_tk.get_tk_widget().grid(column=2, row=1)

root.mainloop()
