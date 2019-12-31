from __future__ import unicode_literals, division, print_function

# built in modules
import os
import sys
import time
import codecs
import shutil
import argparse
from six.moves import input

# project modules
from toolbox import countlines, CuiSemTypesDB, SimstringDBWriter, mkdir
from constants import HEADERS_MRCONSO, HEADERS_MRSTY, LANGUAGES

try:
    from unidecode import unidecode
except ImportError:
    pass


def get_semantic_types(path, headers):
    sem_types = {}
    with codecs.open(path, encoding='utf-8') as f:
        for i, ln in enumerate(f):
            content = dict(zip(headers, ln.strip().split('|')))

            sem_types.setdefault(content['cui'], []).append(content['sty'])

    return sem_types


def get_mrconso_iterator(path, headers, lang='ENG'):
    with codecs.open(path, encoding='utf-8') as f:
        for i, ln in enumerate(f):
            content = dict(zip(headers, ln.strip().split('|')))

            if content['lat'] != lang:
                continue

            yield content


def extract_from_mrconso(
        mrconso_path, mrsty_path, opts,
        mrconso_header=HEADERS_MRCONSO, mrsty_header=HEADERS_MRSTY):

    start = time.time()
    print('loading semantic types...', end=' ')
    sys.stdout.flush()
    sem_types = get_semantic_types(mrsty_path, mrsty_header)
    print('done in {:.2f} s'.format(time.time() - start))

    start = time.time()

    mrconso_iterator = get_mrconso_iterator(
        mrconso_path, mrconso_header, opts.language
    )

    total = countlines(mrconso_path)

    processed = set()
    i = 0

    for content in mrconso_iterator:
        i += 1

        if i % 100000 == 0:
            delta = time.time() - start
            status = (
                '{:,} in {:.2f} s ({:.2%}, {:.1e} s / term)'
                ''.format(i, delta, i / total, delta / i if i > 0 else 0)
            )
            print(status)

        concept_text = content['str'].strip()
        cui = content['cui']
        preferred = 1 if content['ispref'] else 0

        if opts.lowercase:
            concept_text = concept_text.lower()

        if opts.normalize_unicode:
            concept_text = unidecode(concept_text)

        if (cui, concept_text) in processed:
            continue
        else:
            processed.add((cui, concept_text))

        yield (concept_text, cui, sem_types[cui], preferred)

    delta = time.time() - start
    status = (
        '\nCOMPLETED: {:,} in {:.2f} s ({:.1e} s / term)'
        ''.format(i, delta, i / total, delta / i if i > 0 else 0)
    )
    print(status)


def parse_and_encode_ngrams(extracted_it):
    # Create destination directories for the two databases
    #mkdir(simstring_dir)
    #mkdir(cuisty_dir)

    #ss_db = SimstringDBWriter(simstring_dir)
    #cuisty_db = CuiSemTypesDB(cuisty_dir)

    simstring_terms = set()

    for i, (term, cui, stys, preferred) in enumerate(extracted_it, start=1):
    
        term_lower = term.lower()
        
        target_hit = False
        
        #if 'rectal' in term_lower and 'exam' in term_lower:
        #    target_hit = True
        #elif 'colon' in term_lower and 'mucosa' in term_lower:
        #    target_hit = True
        
        if cui in set(['C1384593','C0199900']):
            target_hit = True
        elif cui in set(['C0227349']):
            target_hit = True
            
        if target_hit:
            print('TARGET : Term : [{0}], CUI : [{1}], stys : [{2}]'.format(term, cui, stys)) 
    
        if term not in simstring_terms:
            #ss_db.insert(term)
            simstring_terms.add(term)

        #cuisty_db.insert(term, cui, stys, preferred)


def driver(opts):
    mrconso_path = os.path.join(opts.umls_installation_path, 'MRCONSO.RRF')
    mrsty_path = os.path.join(opts.umls_installation_path, 'MRSTY.RRF')

    mrconso_iterator = extract_from_mrconso(mrconso_path, mrsty_path, opts)

    parse_and_encode_ngrams(mrconso_iterator)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument(
        'umls_installation_path',
        help=('Location of UMLS installation files (`MRCONSO.RRF` and '
              '`MRSTY.RRF` files)')
    )
    ap.add_argument(
        '-L', '--lowercase', action='store_true',
        help='Consider only lowercase version of tokens'
    )
    ap.add_argument(
        '-U', '--normalize-unicode', action='store_true',
        help='Normalize unicode strings to their closest ASCII representation'
    )
    ap.add_argument(
        '-E', '--language', default='ENG', choices=LANGUAGES,
        help='Extract concepts of the specified language'
    )
    opts = ap.parse_args()

driver(opts)
