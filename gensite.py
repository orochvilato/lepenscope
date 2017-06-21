# -*- coding: utf-8 -*-
import requests
import json
import jinja2
import os

APIKEY = 'AIzaSyAl3tgYstQjvgM0krud4pz-PxCo-CXK3I0'

pics = {}
import re
def loadImages():
    loadedimages = os.listdir('images/')
    r = requests.get('https://www.googleapis.com/drive/v3/files?q="0BxG9i5BMTacqRl8yMU9SbW5PY0U"+in+parents&key=%s' % APIKEY)
    print r.content
    images = json.loads(r.content)['files']
    for image in images:
        id = re.match(r'photo_([^\.]+).[a-z]+|logo_([^\.]+).[a-z]+',image['name']).groups()
        if id[0]:
            pics[id[0].lower()] = image['name']
        else:
            pics[id[1].lower()] = image['name']


        if image['name'].encode('utf8') in loadedimages:
            continue

        r = requests.get('https://drive.google.com/uc?id='+image['id']+'&export=download')


        open('images/%s' % image['name'],'w').write(r.content)

loadImages()
candidats = []
import requests
response = requests.get('https://docs.google.com/spreadsheets/d/1FFz6SUbp1NzpijHxYXBqMkOdjpui6V5fPP5wp4C7CBU/export?format=xlsx&id=1FFz6SUbp1NzpijHxYXBqMkOdjpui6V5fPP5wp4C7CBU')
from openpyxl import load_workbook
from cStringIO import StringIO
from textwrap import wrap

f = StringIO(response.content)
wb = load_workbook(f)
wsPers = wb[u'Personnalités']
wsMouv = wb['Mouvements']
wsLien = wb['Liens']
wsLege = wb[u'Légende']


couleurs = {
    'Souverainiste':'#374682',
    'Identitaire':'#915537',
    'Intégriste': '#913773'
}
couleur_autres = '#414141'
personnes = {}
mouvements = {}
liens = []
id = 1

import unicodedata
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def getId(n):
    return n.lower().replace('-','').replace(' ','')

elements = {'nodes':[],'edges':[]}

nodeWeights = {}
for i,row in enumerate(wsLien.rows):
    if i<2:
        continue
    nodeWeights[row[0].value] = nodeWeights.get(row[0].value,0) + 1
    nodeWeights[row[1].value] = nodeWeights.get(row[1].value,0) + 1
    elements['edges'].append({'data':{'source':row[0].value,'target':row[1].value}})

categories = []
nodesimages = []

for i,row in enumerate(wsLege.rows):
    if i<2:
        continue
    categories.append(dict(id=strip_accents(row[2].value),nom=row[2].value,couleur=row[0].value))

for i,row in enumerate(wsPers.rows):
    if i<2:
        continue
    idname = getId(row[0].value)
    node = {'data':
                {'id':row[0].value,
                 'label':row[0].value,
                 'type':'personne',
                 'cat':row[1].value,
                 'poids':nodeWeights.get(row[0].value,0)
                }}
    if idname in pics.keys():
        node['data'].update({'haspic':1})
        nodesimages.append(dict(id=row[0].value,image='images/'+pics[idname]))
    elements['nodes'].append(node)

for i,row in enumerate(wsMouv.rows):
    if i<2:
        continue
    idname = getId(row[0].value)
    node = {'data':
                {'id':row[0].value,
                 'label':row[0].value,
                 'type':'mouvement',
                 'cat':row[1].value,
                 'poids':nodeWeights.get(row[0].value,0)
                }}
    if idname in pics.keys():
        node['data'].update({'haspic':1})
        nodesimages.append(dict(id=row[0].value,image='images/'+pics[idname]))

    elements['nodes'].append(node)



import json
open('reseau/reseau.json','w').write(json.dumps({'elements':elements}, indent=4, separators=(',', ': ')))


def renderTemplate(tpl_path, **context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(**context)




from jinja2 import Environment, PackageLoader, select_autoescape,FileSystemLoader
env = Environment(
    loader=FileSystemLoader('./templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
open('reseau/reseau.cycss','w').write(env.get_template('reseautmpl.cycss').render(categories=categories,nodesimages=nodesimages).encode('utf-8'))
open('js/lepenscope.js','w').write(env.get_template('lepenscopetmpl.js').render(categories=categories).encode('utf-8'))
open('index.html','w').write(env.get_template('indextmpl.html').render(categories=categories).encode('utf-8'))
#open('reseau.html','w').write(env.get_template('reseautempl.html').render(nodes=nodes,edges=edges).encode('utf-8'))
