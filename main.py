import re, os, sys
from prettytable import PrettyTable

#TODO: folder = input()
folder = 'Александр_Иоффе'

# 2 файла в папке с именем-фамилией
flag = True
name1 = name2 = ''
for file_name in os.listdir('data/' + folder):
    if '.csv' in file_name:
        if flag:
            name1 = file_name
            flag = False
        else:
            name2 = file_name

print(name1, name2)

if name1 == '' or name2 == '':
    print("Error: can't found 2 .csv files")
    sys.exit(1)

with open('data/' + folder + '/' + name1, 'r') as f:
    file1 = f.read().split('\n')

with open('data/' + folder + '/' + name2, 'r') as f:
    file2 = f.read().split('\n')


def handle_table(file):
    file[0] = re.sub(', ', '. ', file[0])
    for i in range(len(file)):
        file[i] = file[i].split(',')

    titles = ['Урок №']
    for el in file[0][1:]:
        if 'Урок' in el:
            el = re.sub(' ?Урок', '', el)
            titles.append(re.sub('\xa0', ' ', el))
        else:
            titles.append(el)
    table = [titles]
    for lesson in file[1:]:
        line = [lesson[0]]
        for i in range(1, len(lesson)):
            if i % 3 == 1: # Смотрел ли и как
                if lesson[i] == '---x---':
                    line.append("No")
                elif lesson[i] == 'онлайн':
                    line.append("Online")
                elif lesson[i] == 'видео':
                    line.append("Replay")
                else:
                    line.append('No')
            elif i % 3 == 2:
                lesson[i] = re.search('">[\w/-]+</', lesson[i])
                if lesson[i] != None:
                    line.append(re.sub('-', '0', lesson[i].group(0)[2:-2]))
                else:
                    line.append('')
            else:
                line.append(lesson[i])
        table.append(line)
    return table


def compare_tables(table1, table2):
    table = []
    table1, table2 = table1[1:], table2[1:]
    for i in range(max(len(table1), len(table2))):
        # Проверяем на разные длины таблиц
        if i == len(table1):
            table.append(table2[i])
            break
        elif i == len(table2):
            table.append(table1[i])
            break

        table.append([])
        table[i].append(table1[i][0]) # Нумерация

        for j in range(1, len(table1[i])):
            el1 = table1[i][j]
            el2 = table2[i][j]
            if j % 3 == 1:
                if el1 == el2:
                    table[i].append('---')
                else:
                    if el1 == 'No':
                        table[i].append(el2)
                    else:
                        table[i].append(el1)
            else:
                if el1 == el2:
                    table[i].append('---')
                elif el1 == '':
                    table[i].append(el2 + '(-)')
                elif el2 == '':
                    table[i].append(el1 + '(-)')
                else:
                    if j % 3 == 2:
                        score1 = int(el1.split('/')[0])
                        score2 = int(el2.split('/')[0])
                    else:
                        score1 = float(el1.split('/')[0])
                        score2 = float(el2.split('/')[0])
                    table[i].append(str(max(score1, score2)) + '(' + str(min(score1, score2)) + ')/'
                                    + el1.split('/')[1])
    return table




table1 = handle_table(file1)
table2 = handle_table(file2)
table = compare_tables(table1, table2)
for el in table1:
    print(el)
pt = PrettyTable()
pt._set_field_names(table1[0])
for el in table:
    pt.add_row(el)
print(pt)

"""

for i in range(1, min(len(table1), len(table2))):
    line = [table1[i][0]]
    """
