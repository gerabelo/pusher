'''
Gera um dicionario de termos a partir da colecao facebook
'''

import time, re
from pymongo import MongoClient, TEXT
from bs4 import BeautifulSoup

ts = time.time()

client = MongoClient("mongodb://localhost:27017")
db_src = client['facebook']
db_dst = client['phones']
collection_dst = db_dst['phones']

# sources = ['ACriticaCom','UOLNoticias','bncplay','classificadosam','classificadosmanaus','compraevendamanaus','g1','radiocbn']
sources = ['ACriticaCom','bncplay']

a=0
phones = [[],[]]

for source in sources:
    print('\n',source)
    data = db_src[source]
    # db_dst.create_index([('phone',TEXT)],unique=True)
    # db_dst.create_index([('phone',TEXT)],name='search_index', default_language='portuguese')

    docs = data.find({})
    for doc in docs:
        soup = BeautifulSoup(doc.get("publicacao"), 'html.parser')
        post_message = soup.find("div",{"data-testid":"post_message"})
        if post_message:
            paragraphs = post_message.find_all("p")
            quote = ''
            if paragraphs:
                for paragraph in paragraphs:
                    quote += paragraph.get_text().lower()+' '

            terms = quote.split()
            for term in terms:
                phone = re.search("(\(?\d{2}\)?\s)?(\d{4,5}[-]{0,1}[_]{0,1}\d{4})",term)
                if phone:
                    # word = re.sub(r'[a-záàâãéèêíïóôõöúçñ]+','',word,flags=re.I)
                    # word = word.replace('.','').replace(',','').replace('!','').replace(':','').replace('-','').replace('_','').replace('/','').replace('(')
                    results = re.findall(r'\d',term)
                    term = ''.join(results)                        
                    print('phone: ',term)
                    a+=1
                    i = len(phones[0])
                    print(i)
                    j = 0
                    while i > 0:
                        i -= 1
                        if phones[0][i] == term:
                            j = 1
                    if j == 0:
                        phones[0].append(term)
                        phones[1].append(quote)
                        # phones[1].append(doc.get("publicacao")) #post_message
i = len(phones[0])
print(i)
while i > 0:
    i -= 1
    # print(phones[0][i],phones[1][i])
    try:
        collection_dst.insert_one({"phone":phones[0][i],"publicacao":phones[1][i]})
    except Exception as e:
        print(e)