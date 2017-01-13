import re, os, sys
from prettytable import PrettyTable


def open_files():
    for i in range(3):
        print("Введите имя папки")
        dir = input()
        if dir in os.listdir('data'):
            break
        else:
            print("Данной папки не существует. Попробуйте ещё раз.")
    else:
        print("Попытки закончились.")
        exit()
    dir = 'data/' + dir

    for i in range(3):
        print("Введите имя первого файла:")
        name1 = input()
        if name1 in os.listdir(dir):
            break
        else:
            print("Данного файла не существует. Попробуйте ещё раз.")
    else:
        print("Попытки закончились.")
        exit()

    for i in range(3):
        print("Введите имя второго файла")
        name2 = input()
        if name2 in os.listdir(dir):
            break
        else:
            print("Данного файла не существует. Попробуйте ещё раз.")
    else:
        print("Попытки закончились.")
        exit()

    with open(dir + '/' + name1, 'r', encoding="UTF-8") as f:
        file1 = f.read().split('\n')

    with open(dir + '/' + name2, 'r', encoding="UTF-8") as f:
        file2 = f.read().split('\n')

    return [file1, file2]


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
                    line.append("Not seen")
                elif lesson[i] == 'онлайн':
                    line.append("Online")
                elif lesson[i] == 'видео':
                    line.append("Replay")
                else:
                    line.append('')
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


def compare_tables(table1, table2, hide_old_data=True):
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
                if ((el1 == '' or el1 == 'Not seen') and (el2 == '' or el2 == 'Not seen') or el1 == el2) and hide_old_data:
                    table[i].append('---')
                else:
                    if el1 == 'Not seen' or el1 == '':
                        if el2 != 'Not seen' and el2 != '':
                            table[i].append(el2 + '(+)')
                        else:
                            table[i].append(el2)
                    else:
                        table[i].append(el1)
            else:
                if el1 == el2 and hide_old_data:
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
                    if el1 != el2:
                        table[i].append(str(max(score1, score2)) + '(' + str(min(score1, score2)) + ')/'
                                    + el1.split('/')[1])
                    else:
                        table[i].append(str(score1) + '/' + el1.split('/')[1])
    return table


def print_course_progress(table, column_names):
    course_stats = {}
    for i in range(len(column_names)):
        if '.' in column_names[i]:
            course_stats[column_names[i]] = {'seen': [0, 0, 0], 'solved': [0, 0, 0]}
    for row in table:
        for i in range(1, len(row)):
            j = i - 1
            if i % 3 == 1:  # Watching stats
                if row[i] != '':
                    course_stats[column_names[j]]['seen'][2] += 1
                    if row[i] != 'Not seen':
                        course_stats[column_names[j]]['seen'][0] += 1
                        if '+' not in row[i]:
                            course_stats[column_names[j]]['seen'][1] += 1
            elif i % 3 == 2:  # Solving stats
                k = j - 1
                if row[i] != '(-)' and row[i] != '':
                    course_stats[column_names[k]]['solved'][2] += 1
                    if '(' in row[i]:
                        p1 = row[i].find('(')
                        p2 = row[i].find(')')
                        solved_new = int(row[i][:p1])
                        solved_old = int(row[i][p1+1:p2])
                        total = int(row[i][p2+2:])
                        course_stats[column_names[k]]['solved'][0] += float(solved_new) / total
                        course_stats[column_names[k]]['solved'][1] += float(solved_old) / total
                    else:
                        p = row[i].find('/')
                        solved = int(row[i][:p])
                        total = int(row[i][p+1:])
                        course_stats[column_names[k]]['solved'][0] += float(solved) / total
                        course_stats[column_names[k]]['solved'][1] += float(solved) / total

    # Создаем словарь {предмет: иноформация по курсам} для упрощенного вывода
    stats = {}
    for course in course_stats.keys():
        subject = course[:course.find('.')]
        course_name = course[course.find('.')+2:]
        if subject not in stats:
            stats[subject] = subject + ':\n'
        if course_stats[course]['seen'][0] == course_stats[course]['seen'][1]:
            stats[subject] += '{0}  — просмотрено {1}/{2}, '.format(course_name, course_stats[course]['seen'][0],
                                                                 course_stats[course]['seen'][2])
        else:
            stats[subject] += '{0}  — просмотрено {1}({2})/{3}, '.format(course_name, course_stats[course]['seen'][0],
                                                                     course_stats[course]['seen'][1],
                                                                     course_stats[course]['seen'][2])
        if course_stats[course]['solved'][0] == course_stats[course]['solved'][1]:
            stats[subject] += 'сделано {0:.1f}/{1} занятий\n'.format(course_stats[course]['solved'][0],
                                                       course_stats[course]['solved'][2])
        else:
            stats[subject] += 'сделано {0:.1f}({1:.1f})/{2} занятий\n'.format(course_stats[course]['solved'][0],
                                                           course_stats[course]['solved'][1],
                                                           course_stats[course]['solved'][2])

    # Выводим словарь
    for subject in stats.keys():
        print(stats[subject])

while True:
    print("Сравнение таблиц выгрузки")

    file1, file2 = open_files()
    table1 = handle_table(file1)
    table2 = handle_table(file2)
    detailed_table = compare_tables(table1.copy(), table2.copy(), False)
    print_course_progress(detailed_table, table1[0][1:])

    table = compare_tables(table1, table2)
    pt = PrettyTable()
    pt._set_field_names(table1[0])
    for el in table:
        pt.add_row(el)
    print(pt)
    print()
