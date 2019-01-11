import csv 
import requests 
import xml.etree.ElementTree as ET 
import sys
import json

# check to see if PMID is given
if len(sys.argv) < 2:
    raise ValueError("requires PMID as first argument")
    
# get PMID
pmid = sys.argv[1]
print('retrieving PMID', pmid)

def get_abstract(pmid):
    # make HTTP request to Pubmed
    url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=%s&retmode=xml' % pmid
    resp = requests.get(url) 
    # verify response is OK
    if resp.status_code != requests.codes.ok:
        raise ValueError('Error retrieving PubMed data. Received HTTP code' + str(resp.status_code))

    print('PubMed data received')

    # parse XML
    root = ET.fromstring(resp.text)
    abstract = root.find('PubmedArticle/MedlineCitation/Article/Abstract/AbstractText')

    # verify abstract exists
    if not abstract:
        raise ValueError('Cannot find abstract in XML')

    # join abstract text
    abstract_text = ' '.join(abstract.itertext())

    return abstract_text


def save_json(abstract_text):
    # create REACH request parameters
    params = {
        'text': abstract_text,
        'output': 'fries',
    }

    # make post request
    r = requests.post('http://agathon.sista.arizona.edu:8080/odinweb/api/text', params=params)

    # parse json data
    data = json.loads(r.text)

    # print statisics
    print('REACH data statistics:')
    for key in data:
        print(key, len(data[key]), 'elements')
    print()

    # save data
    filename = pmid + '.json'
    print ('saving', filename)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(r.text)

abstract_text = get_abstract(pmid)
save_json(abstract_text)