#!/usr/bin/python3

import csv
import argparse
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

class buyer_parser:
  def load_csv(self, filename):
    # ordered by country as key
    buyers = dict()

    # tsv file, tab delimited, no escaping characters
    with open(filename) as tsvfile:
      buyreader = csv.DictReader(tsvfile, delimiter='\t')

      for row in buyreader:
        try:
          buyers[row['countryname']].append(row['buyer'].upper())
        except KeyError:
          buyers[row['countryname']] = list()
          buyers[row['countryname']].append(row['buyer'].upper())

    return buyers

  # takes list of buyers, displays matches
  def mash_list(self, buyers, short_threshold, long_threshold, short_size, stemming):
    match_list = []
    for i, buyer in enumerate(buyers):
      if(buyer not in match_list):
        match_list.append(buyer)
        # excl_buyers is list of buyers excluding current check
        excl_buyers = buyers[:i] + buyers[i+1 :]
        # stem if stemming > 0
        if(stemming > 0): excl_buyers = filter(lambda x: x.startswith(buyer[:stemming]), excl_buyers)
        # threshold depends on length of buyer name
        threshold = long_threshold if len(buyer) > short_size else short_threshold

        sl = process.extractWithoutOrder(buyer, excl_buyers, scorer=fuzz.token_sort_ratio, score_cutoff=threshold)
        matches = sorted(sl, key=lambda i: i[1], reverse=True)
        for match in matches:
          match_list.append(match[0])
          print('\t'.join([buyer, match[0], str(match[1])]))

parser = argparse.ArgumentParser(description='Finds matches above a certain threshold in a tsv file')
parser.add_argument('filename', metavar='file', help='tsv file to be processed')
parser.add_argument('short_threshold', metavar='short', type=int, help='match threshold 0-100 for short names')
parser.add_argument('long_threshold', metavar='long', type=int, help='match threshold 0-100 for long names')
parser.add_argument('short_length', metavar='length', type=int, help='length (inclusive) of short names')
parser.add_argument('country', help='country')
parser.add_argument('-s', metavar='stemming', type=int, default=0, help='number of letters to stem (0 for no stemming)')

args = parser.parse_args()
b = buyer_parser()
buyers = b.load_csv(args.filename)
b.mash_list(buyers[args.country.upper()], args.short_threshold, args.long_threshold, args.short_length, args.s)
