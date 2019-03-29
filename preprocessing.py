# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 18:47:54 2019

@author: hariramk
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import csv
import fnmatch
import logging
import os
import shutil
import time

from xml.etree import ElementTree


def load_pan_data(xmls_directory, truth_path, write_to_txt_files=False, txts_destination_directory=True):
    xml_filenames = sorted(os.listdir(xmls_directory))
    author_ids = []
    for xml_filename in xml_filenames:
        author_ids.append(xml_filename[:-4])

    if truth_path is None:
        print("*truth_path* is None => Skipped loading the truth")
        truths = None
    else:
        truths = load_truth(truth_path, author_ids)

    if write_to_txt_files:
        print("The parsed XMLs will also be written to TXT files.")
        os.makedirs(txts_destination_directory, exist_ok=True)
    original_tweet_lengths = []
    merged_tweets_of_authors = []

    for author_index, xml_filename in enumerate(xml_filenames):
        if not fnmatch.fnmatch(xml_filename, '*.xml'):
            print("Encountered a non-XML file inside the directory: %s >>> The program will now exit.",
                  xml_filename)
            raise RuntimeError('Encountered a non-XML file inside the directory: %s' % xml_filename)
        tree = ElementTree.parse(os.path.join(xmls_directory, xml_filename),
                                 parser=ElementTree.XMLParser(encoding="utf-8"))
        root = tree.getroot()
        original_tweet_lengths.append([])
        tweets_of_this_author = []  # Create an empty list
        for child in root[0]:
            tweet = child.text
            original_tweet_lengths[author_index].append(len(tweet))
            tweet = tweet.replace('\n', " <LineFeed> ")
            tweets_of_this_author.append(tweet)
        if write_to_txt_files:
            with open(os.path.join(txts_destination_directory, author_ids[author_index] + ".txt"),
                      'w', encoding="utf-8") as txt_output_file:
                txt_output_file.write('\n'.join(tweets_of_this_author))
        merged_tweets_of_this_author = " <EndOfTweet> ".join(tweets_of_this_author) + " <EndOfTweet>"
        merged_tweets_of_authors.append(merged_tweets_of_this_author)

    print("@ %.2f seconds: Finished loading the dataset", time.process_time())

    return merged_tweets_of_authors, truths, author_ids, original_tweet_lengths


def load_truth(truth_path, author_ids):

    temp_sorted_author_ids_and_truths = []
    with open(truth_path, 'r') as truth_file:
        for line in sorted(truth_file):
            line = line.rstrip('\n')
            temp_sorted_author_ids_and_truths.append(line.split(":::"))

    truths = []
    for i, row in enumerate(temp_sorted_author_ids_and_truths):
        if row[0] == author_ids[i]:
            truths.append(row[1])
        else:
            print("Failed to sync the order of the Truth list and the Author ID list."
                         "Row number: %d >>> The program will now exit.", i)
            raise RuntimeError('Failed to sync the order of the Truth list and the Author ID list. Row number: %d' % i)

    return truths

def load_flame_dictionary(path="data/Flame_Dictionary.txt"):

    print("Loading the Flame Dictionary from path: %s", os.path.realpath(path))

    flame_dictionary = {}
    duplicates = []
    flame_expressions_dict = {1: [], 2: [], 3: [], 4: [], 5: []}  # Create a dictionary of 5 empty lists

    with open(path, 'r') as flame_dictionary_file:
        for line in flame_dictionary_file:
            line = line.rstrip('\n')

            flame_level = int(line[0])
            expression = line[2:]

            if expression in flame_dictionary:
                duplicates.append(expression)
            else:
                flame_dictionary[expression] = flame_level
                flame_expressions_dict[flame_level].append(expression)

    if len(duplicates) > 0:
        print("%d duplicate expressions found in the Flame Dictionary: %s"+len(duplicates) + duplicates)

    return flame_dictionary, flame_expressions_dict


def write_predictions_to_xmls(author_ids_test, y_predicted, xmls_destination_main_directory, language_code):
    """Write predictions to XML files
    This function is only used in **TIRA** evaluation.
    It writes the predicted results to XML files with the following format:
        <author id="author-id" lang="en|es" gender_txt="female|male" gender_img="N/A" gender_comb="N/A" />
    """

    # Add the alpha-2 language code (“en” or “es”) subdirectory to the end of the output directory
    xmls_destination_directory = os.path.join(xmls_destination_main_directory, language_code)

    # Create the directory if it does not exist.
    os.makedirs(xmls_destination_directory, exist_ok=True)

    # Iterate over authors in the test set
    for author_id, predicted_gender in zip(author_ids_test, y_predicted):
        # Create an *Element* object with the desired attributes
        root = ElementTree.Element('author', attrib={'id': author_id,
                                                     'lang': language_code,
                                                     'gender_txt': predicted_gender,
                                                     'gender_img': "N/A",
                                                     'gender_comb': "N/A",
                                                     })
        # Create an ElementTree object
        tree = ElementTree.ElementTree(root)
        # Write the tree to an XML file
        tree.write(os.path.join(xmls_destination_directory, author_id + ".xml"))
        # ↳ ElementTree sorts the dictionary of attributes by name before writing the tree to file.
        # ↳ The final file would look like this:
        # <author gender_comb="N/A" gender_img="N/A" gender_txt="female|male" id="author-id" lang="en|es" />
    logger.info("@ %.2f seconds: Finished writing the predictions to XML files", time.process_time())


def write_feature_importance_rankings_to_csv(sorted_feature_weights, sorted_feature_names, log_file_path):
    """Write the feature importance rankings to a CSV file.
    This function writes the feature importance rankings to a CSV file, next to the log file.
    Refer to the docstring of the *write_iterable_to_csv()* function.
    """

    # Determine the path of the output CSV file based on the path of the log file, such that the leading date and
    # time of the two filenames are the same.
    log_file_directory = os.path.dirname(log_file_path)
    log_file_name_without_extension = os.path.splitext(os.path.basename(log_file_path))[0]
    CSV_PATH = os.path.join(log_file_directory, log_file_name_without_extension + "; Feature importance rankings.csv")

    # Create the directory if it does not exist.
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

    # Write to the CSV file
    with open(CSV_PATH, 'w', newline='', encoding="utf-8") as csv_output_file:
        csv_writer = csv.writer(csv_output_file)
        csv_writer.writerow(["Feature weights:", "Feature names:"])
        csv_writer.writerows(zip(sorted_feature_weights, sorted_feature_names))

    logger.info('List of features based on their importance in the classification model (absolute feature weight) '
                'was written to CSV file: "%s"', CSV_PATH)


def write_iterable_to_csv(iterable, iterable_name, log_file_path):
    """Write an iterable to a CSV file.
    This function writes any iterable object to a CSV file next to the log file.
    - You can get *log_file_path* by calling *logger.handlers[1].baseFilename* in the root module, assuming that
    the file handler is the second handler of the logger.
    • CSV Writer objects remarks:
    - *csvwriter.writerow(row)*:   A row must be an iterable of strings or numbers.
    - *csvwriter.writerows(rows)*: *rows* must be a list of row objects, described above.
    """

    # Determine the path of the output CSV file based on the path of the log file, such that the leading date and
    # time of the two filenames are the same.
    log_file_directory = os.path.dirname(log_file_path)
    log_file_name_without_extension = os.path.splitext(os.path.basename(log_file_path))[0]
    CSV_PATH = os.path.join(log_file_directory, log_file_name_without_extension + "; " + iterable_name + ".csv")

    # • Find out if the iterable is an “iterable of iterables”. For example, [[1, 2], [3, 4]] is an iterable
    # of iterables—each item in it is also an iterable; however, [1, 2, 3] isn't.

    # Select the first item in the iterable. We will only test this item.
    item = iterable[0]

    # The following is “the try statement”.
    try:
        iterator = iter(item)
        # ↳ This will raise a TypeError exception if *item* is not iterable.
    except TypeError:
        # This means *item* is not iterable.
        item_is_iterable = False
    else:
        # This means *item* is an iterable.
        item_is_iterable = True

    # If *item* is a string, it means it escaped from us! Strings are considered iterables, but here, we are
    # looking for iterables such as lists and tuples, not strings.

    # If *item* is not iterable or it is a string, convert *iterable* to a list of lists of one item each.
    # For example: (1, 2, 3) → [[1], [2], [3]]
    if not item_is_iterable or isinstance(item, str):
        iterable = [[item] for item in iterable]
    # Now *iterable* is an “iterable of iterables”!

    # Create the directory if it does not exist.
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

    # Write to the CSV file
    with open(CSV_PATH, 'w', newline='', encoding="utf-8") as csv_output_file:
        csv_writer = csv.writer(csv_output_file)
        csv_writer.writerow([iterable_name])
        csv_writer.writerows(iterable)

    logger.info('%s was written to CSV file: "%s"', iterable_name, CSV_PATH)


'''
The following lines will be executed any time this .py file is run as a script or imported as a module.
'''
# Create a logger object. The root logger would be the parent of this logger
# Note that if you run this .py file as a script, this logger will not function, because it is not configured.
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # The following lines will be executed only if this .py file is run as a script,
    # and not if it is imported as a module.
    
    directory = 'U:/Desktop/textAnalytics/New folder/pan19-author-profiling-training-2019-02-18-20190302T192830Z-001/pan19-author-profiling-training-2019-02-18'
    merged_tweets_of_authors, truths, author_ids, original_tweet_lengths = load_pan_data(directory+'/en', directory+'/en-truth/truth.txt', False, directory+'/txtFiles')
    print("Module was executed directly.")
    print('merged_tweets_of_authors',merged_tweets_of_authors)

