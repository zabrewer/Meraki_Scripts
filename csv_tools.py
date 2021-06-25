import csv
import itertools
import re

__author__ = 'Zach Brewer'
__email__ = 'zbrewer@cisco.com'
__version__ = '0.0.8'
__license__ = 'MIT'

# cleans up the first line of an iterator (i.e. CSV headers)
def clean_firstrow(iterator):
    return itertools.chain([next(iterator).lower().replace(' ', '').replace('_', '').replace('\ufeff', '')], iterator)


# def read_csv(filename, req_headers, valid_headers):
def read_csv(filename, req_headers):
  
    """
    reads CSV file and verifies that headers are valid (accepted by API).

    Args:
    filename: The csv filename to use.
    req_headers: Minimum headers to validate that are used in the CSV file.
    Returns:
    None
    """
    # csv_dict is a lazy iterator so is exausted after iterating over it once.
    # this is the most memory efficient way I could come up with although it is duplicated.
    # TODO: refactor this
    # TODO: check for file existence

    csv_dict = csv.DictReader(clean_firstrow(open(filename, mode='r', encoding='utf-8-sig')))
    total_rows = sum(1 for row in csv_dict)  # fileObject is your csv.reader

    # reopening the file - other options are copy the DictReader to another dict
    # or start back at f(0) on a file object
    csv_dict = csv.DictReader(clean_firstrow(open(filename)))

    headers = csv_dict.fieldnames
    req_headers_clean = []
    
    # clean up required headers so it matches lower case + cleaned up dict headers
    for item in req_headers:
        clean = item.lower().replace(' ', '').replace('_','')
        req_headers_clean.append(clean)

    header_diff = [i for i in headers + req_headers_clean if i not in headers]

    # only prints obj type when unpacking - lambda, iterable unpacking, list comp, etc.
    missing = ' '.join(map(str, header_diff))

    if header_diff:
        print(f'The following required headers were not found in the file "{filename}": {missing}')
    else:
        return csv_dict, total_rows

def is_validmac(str):
    regex = ('^([0-9A-Fa-f]{2}[:-])' +
             '{5}([0-9A-Fa-f]{2})|' +
             '([0-9a-fA-F]{4}\\.' +
             '[0-9a-fA-F]{4}\\.' +
             '[0-9a-fA-F]{4})$')
             
    p = re.compile(regex)

    if (str is None):
        return False

    return bool((re.match(p, str)))
