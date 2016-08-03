#! /usr/bin/python

# Author: Geomar Manzano

import json         # to parse the json files
import math         # math.log used for entropy calculation
import copy         # to copy sets for recursion
import sys          # to set recursion limit
import operator     # for compact max val in dict finding

sys.setrecursionlimit(10000)

#--------------------------------------------------------------------------------

# [Required Classes and Functions]

# Binary Tree
class SimpleTree():
    def __init__(self, value):
        self.left = None
        self.right = None
        self.value = value
    def get_left(self):
        return self.left
    def get_right(self):
        return self.right
    def set_value(self, value):
        self.value = value
    def insert_left(self, new_node):
        self.left = new_node
    def insert_right(self, new_node):
        self.right = new_node
    def has_children(self):
        return (self.left != None or self.right != None)

# Prints a given SimpleTree
def print_tree(fp, tree, level = 0):
    if tree != None:
        fp.write(str((tree.value).encode('ascii','ignore')) + \
                 ' ' + str(level) + '\n')
        print_tree(fp, tree.left, level + 1)
        print_tree(fp, tree.right, level + 1)

# Calculates entropy
def calc_entropy(num_zeroes, num_ones, dist_zeros, dist_ones):
    totalNum = float(num_zeroes + num_ones)
    zero_info = 0.0
    for num in dist_zeros:
        if num == 0:
            continue        
        zero_info += (-float(num)/num_zeroes) * \
                     math.log(float(num)/num_zeroes, 2)
    one_info = 0.0
    for num in dist_ones:
        if num == 0:
            continue
        one_info += (-float(num)/num_ones) * math.log(float(num)/num_ones, 2)
    entropy = (float(num_zeroes)/totalNum) * \
              zero_info + (float(num_ones)/totalNum) * one_info
    return entropy

# Calculates the best ingredient to split on given the rows and columns
# and returns a tree with the node value set to the ideal ingredient
def split_matrix(rows, columns, ingredient_tree):
    if len(rows) == 0:
        return None
    cuisines = set([cuisine_dict[row] for row in rows])
    if len(cuisines) == 1:
        ingredient_tree.set_value(cuisines.pop())
        return ingredient_tree
    best_entropy = -1
    best_ingredient = None
    if len(columns) == 1:
        best_ingredient = columns.pop() # e.g. tomatoes
        zero_cuisines = {}
        one_cuisines = {}
        for row in rows:
            x = matrix[row][best_ingredient]
            cuis = cuisine_dict[row]
            if x == 0:
                if cuis in zero_cuisines:
                    zero_cuisines[cuis] = zero_cuisines[cuis] + 1
                else:
                    zero_cuisines[cuis] = 1
            if x == 1:
                if cuis in one_cuisines:
                    one_cuisines[cuis] = one_cuisines[cuis] + 1
                else:
                    one_cuisines[cuis] = 1
        if len(zero_cuisines) == 0: #all 1's
            best_one = max(one_cuisines.iteritems(),
                           key=operator.itemgetter(1))[0]
            ingredient_tree.set_value(best_one)
            return ingredient_tree
        if len(one_cuisines) == 0: #all 0's
            best_zero = max(zero_cuisines.iteritems(),
                            key=operator.itemgetter(1))[0]
            ingredient_tree.set_value(best_zero)
            return ingredient_tree
        best_zero = max(zero_cuisines.iteritems(), key=operator.itemgetter(1))[0]
        best_one = max(one_cuisines.iteritems(), key=operator.itemgetter(1))[0]
        ingredient_tree.set_value(ingredients_list[best_ingredient])
        ingredient_tree.insert_left(SimpleTree(best_zero))
        ingredient_tree.insert_right(SimpleTree(best_one))
        return ingredient_tree
    # for each column/ingredient
    for ingr in columns:
        # counts of zeroes and ones for each ingredient
        counts = [0, 0]
        # distribution of zeroes and ones for each ingredient
        dists = [{}, {}]
        for row in rows:
            # get the value at the matrix
            x = matrix[row][ingr]
            counts[x] += 1
            cuisine = cuisine_dict[row]
            if cuisine in dists[x]:
                dists[x][cuisine] += 1
            else:
                dists[x][cuisine] = 1
        #calculate the entropy for the counts and dists
        entropy = calc_entropy(*(counts + [x.values() for x in dists]))    
        if entropy < best_entropy or best_entropy == -1:
            #print ingr, entropy, best_entropy
            best_ingredient = ingr
            best_entropy = entropy
    # set the splitting ingredient
    print 
    ingredient_tree.set_value(ingredients_list[best_ingredient])
    # get the rows for 0 and 1 for the ingredient
    zero_rows = set()
    one_rows = set()
    for row in rows:
        x = matrix[row][best_ingredient]
        if x == 0:
            zero_rows.add(row)
        else:
            one_rows.add(row)
    print 'SPLITTING ON:', \
        ingredients_list[best_ingredient].encode('ascii','ignore')
    # get remaining columns
    columns.remove(best_ingredient)
    remaining_copy = copy.copy(columns)
    print len(zero_rows),
    print len(one_rows)
    ingredient_tree.insert_left(split_matrix(zero_rows, columns, SimpleTree('')))
    ingredient_tree.insert_right(split_matrix(one_rows, remaining_copy,
                                              SimpleTree('')))
    return ingredient_tree

#--------------------------------------------------------------------------------

# [Initialization Phase]

# Choose from one of the training sets listed below
#   TRAINING_FILENAME = chosenTrainingSet
#
# train.json  = full data set 
# train2.json = very small portion of the data set
# train4.json = quarter of the data set 
# train5.json = half of the data set

TRAINING_FILENAME = 'train.json'
TESTING_FILENAME  = 'test.json'

# Open file and retrieve data
with open(TRAINING_FILENAME) as data_file:    
    data = json.load(data_file)

# Ingredient Set
ingredients_set = set()

# Recipe dictionary in case IDs are needed later
recipe_dict   = {}
cuisine_dict  = {}
id_to_cuisine = {}

# Bag of Words
for d in data:
    ingredients_set.update(d['ingredients'])

# Create a list of all ingredients
ingredients_list = list(ingredients_set)
print ingredients_list
num_ingredients = len(ingredients_list)

# Ingredients dict maps column numbers to ingredients
ingredients_dict = {x:i for i,x in enumerate(ingredients_list)}

matrix = []

i = 0
for d in data:
    # row processing
    row = [0] * num_ingredients
    ingredients = d['ingredients']
    for ingredient in ingredients:
        row[ingredients_dict[ingredient]] = 1
    matrix.append(row)
    
    #ID
    recipe_dict[i] = d['id']
    #cuisine
    cuisine_dict[i] = d['cuisine']
    
    id_to_cuisine[d['id']] = d['cuisine']
    
    i += 1

print 'done with initial file processing: matrix created'

#--------------------------------------------------------------------------------

# [Training Phase]

ingredient_tree = split_matrix(set(range(len(matrix))), set(range(num_ingredients)), SimpleTree(''))

tree_file = open('tree.txt', 'w')
print_tree(tree_file, ingredient_tree)
tree_file.close()

#--------------------------------------------------------------------------------

# [Testing Phase]

results = open('results.csv', 'w')

results.write('id,cuisine\n')

with open(TESTING_FILENAME) as test_file:    
    test_data = json.load(test_file)

sol = {}

for recipe in test_data:
    ingr = set(recipe['ingredients'])
    #traverse tree
    node = ingredient_tree
    while node.has_children():
        if node.value in ingr:
            if node.right != None:
                node = node.right
            else:
                node.value = 'UNKNOWN'
                break
        else:
            if node.left != None:
                node = node.left
            else:
                node.value = 'UNKNOWN'
                break
    print recipe['id'], node.value
    sol[recipe['id']] = node.value

# Write to file
for s, v in sol.iteritems():
    results.write(str(s) + ',' + v + '\n')

results.close()
