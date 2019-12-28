import os
import json
import gita_encode

docx_as_dict = gita_encode.encode_doc(os.path.join('../test_data', 'sample chapter.docx'))
with open('sample chapter.json', 'w') as jsonfile:
    json.dump(docx_as_dict, jsonfile, indent=2)
