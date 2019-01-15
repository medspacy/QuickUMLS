import time
import os

try:
    from quickumls import QuickUMLS
    import constants
except ImportError:
    from .quickumls import QuickUMLS

print('Creating QuickUMLS object...')
    
quickumls_path = r'C:\quickumls\SNOMED_RXNORM_CPT_lowercase'
    
total_iterations = 1
ignore_syntax = False
threshold = 0.7
accepted_semtypes = None
# accepted_semtypes = constants.ACCEPTED_SEMTYPES
    
print('Setting up for semtypes (None means all types) : {}'.format(accepted_semtypes))
    
matcher = QuickUMLS(quickumls_path, accepted_semtypes = accepted_semtypes, threshold = threshold)

print('QuickUMLS object created...')

text_file_path = r'data/colonoscopy-1.txt'
file = open(text_file_path, 'r') 
text = file.read()
file.close()

print('Length of Text : {0} characters'.format(len(text)))

print('About to reprocess this text [{0}] times'.format(total_iterations))

results_list = []
result_count = 0

start_time = time.time()

output_dir = 'output/performance_test'

for i in range(total_iterations):
    if i % 100 == 0:
        print('Progress : [{0}/{1}]'.format(i, total_iterations))

        
    filename = '{0}.csv'.format(i)
    f = open(os.path.join(output_dir, filename), 'w')

    match_results = matcher.match(text, best_match=True, ignore_syntax=ignore_syntax)
    results_list.append(match_results)
    result_count += len(match_results)
    
    header = 'text,start,end,CUI,term,similarity\n'
    f.write(header)
    
    # this is a list of lists
    for match_result in match_results:
        # each match may contain multiple ngram entries
        for ngram_match_dict in match_result:
            #print(ngram_match_dict)
            line = '"{0}",{1},{2},{3},"{4}",{5:.2f}\n'.format(ngram_match_dict['ngram'], 
                ngram_match_dict['start'],
                ngram_match_dict['end'],
                ngram_match_dict['cui'],
                ngram_match_dict['term'],
                ngram_match_dict['similarity'])
            f.write(line)
    
    f.close()
    
    #print('Matching results:')
    #print(match_results)
    
end_time = time.time()

elapsed_time_seconds = end_time - start_time

avg_doc_time_seconds = elapsed_time_seconds / float(len(results_list))

print('Total results received : [{0}]'.format(result_count))
print('Total time for [{0}] documents was [{1}] seconds'.format(len(results_list), elapsed_time_seconds))
print('Avg time per document : [{0}] seconds'.format(avg_doc_time_seconds))

print('DONE with performance test')