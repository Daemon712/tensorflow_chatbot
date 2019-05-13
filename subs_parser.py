import os
import re
import chardet

engCharsPattern = re.compile('[a-zA-Z]')


def process_subs():
    with open('data/raw_lines.txt', 'w') as target:

        for folder_name in os.listdir('subs'):
            for file_name in os.listdir('subs/' + folder_name):
                file_path = 'subs/' + folder_name + '/' + file_name
                with open(file_path, 'r', encoding=predict_encoding(file_path), errors='ignore') as file:
                    while file.readline() and file.readline():  # skip number and time ranges
                        process_text(file, target)  # read text


def process_text(source, target):
    line = source.readline()
    if line and line != '\n':
        if not bool(engCharsPattern.search(line)) and line.find('Нотабеноиде') == -1:
            target.write(line.lower())

        process_text(source, target)


def predict_encoding(file_path, n_lines=20):
    with open(file_path, 'rb') as f:
        raw_data = b''.join([f.readline() for _ in range(n_lines)])

    enc = chardet.detect(raw_data)['encoding']
    # print(file_path + ' - ' + enc)
    if enc == 'MacCyrillic':
        enc = ' windows-1251'
    return enc
