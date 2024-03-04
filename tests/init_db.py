from unittest.mock import patch
from quickumls.install import main
from pathlib import Path
def init(resource_folder='output', quickumls_fp=str(Path('output', 'QuickUMLS_SAMPLE_lowercase_UNQLITE')), force_rebuild=False):
    '''
    Make a demo UMLS dictionary for testing. The following items are using fake CUIs and TUIs.
    '''
    if Path(quickumls_fp).exists() and not force_rebuild:
        return   
    mrconso_text=r'''C0000001|ENG|S|L0000002|VO|S0000895|N|A0000030||||BI|PT|BI00001|dipalmitoyllecithin|2|N|256|
C0000001|ENG|S|L0000002|VO|S0000895|N|A0000031||||BI|PT|BI00001|dipalmitoyl phosphatidylcholine|2|N|256|
C0000002|ENG|S|L0000003|VO|S0000005|N|A0000041||||BI|PT|BI00002|glycosyltransferase|2|N|256|'''
    mrsty_text=r'''C0000001|T191|||||
C0000002|T191|||||'''
    Path(resource_folder,'MRCONSO.RRF').write_text(mrconso_text)
    Path(resource_folder,'MRSTY.RRF').write_text(mrsty_text)
    if Path(quickumls_fp).exists():        
        import shutil
        shutil.rmtree(quickumls_fp)
    Path(quickumls_fp).mkdir(parents=True)
    print('write terminology to quickumls_fp:', Path(quickumls_fp).absolute().resolve())
    test_args=['prog',resource_folder, quickumls_fp, '-L','-d','unqlite']
    with patch('sys.argv', test_args):
        main()    
    
