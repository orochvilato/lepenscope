# -*- coding: utf-8 -*-
import requests
import json
import jinja2
import os

APIKEY = 'AIzaSyB-tQmeF1zWos01WfvFykZq07hO6wBNYDU'

pics = {}
import re
def loadImages():
    loadedimages = os.listdir('images/')
    r = requests.get('https://www.googleapis.com/drive/v3/files?q="0BxG9i5BMTacqRl8yMU9SbW5PY0U"+in+parents&key=%s' % APIKEY)
    images = json.loads(r.content)['files']
    for image in images:
        id = re.match(r'photo_([^\.]+).[a-z]+|logo_([^\.]+).[a-z]+',image['name']).groups()
        if id[0]:
            pics[id[0].lower()] = image['name']
        else:
            pics[id[1].lower()] = image['name']


        if image['name'].encode('utf8') in loadedimages:
            continue
        print "ok"
        r = requests.get('https://drive.google.com/uc?id='+image['id']+'&export=download')


        open('images/%s' % image['name'],'w').write(r.content)

loadImages()
candidats = []
import requests
response = requests.get('https://docs.google.com/spreadsheets/d/1FFz6SUbp1NzpijHxYXBqMkOdjpui6V5fPP5wp4C7CBU/export?format=xlsx&id=1FFz6SUbp1NzpijHxYXBqMkOdjpui6V5fPP5wp4C7CBU')
from openpyxl import load_workbook
from cStringIO import StringIO
f = StringIO(response.content)
wb = load_workbook(f)
wsPers = wb[u'Personnalités']
wsMouv = wb['Mouvements']
wsLien = wb['Liens']
print wb.get_sheet_names()

couleurs = {
    'Souverainiste':'#374682',
    'Identitaire':'#915537',
    'Catholique intégriste': '#913773'
}
couleur_autres = '#414141'
personnes = {}
mouvements = {}
liens = []
id = 1
def formatLabel(l):
    s = l.split(' ')
    label = s[0] + '\n' + ' '.join(s[1:])
    label = '\n'.join(s)
    return label
def getId(n):
    return n.lower().replace('-','').replace(' ','')

for i,row in enumerate(wsPers.rows):
    if i<2:
        continue
    idname = getId(row[0].value)
    node = {'id':id, 'label':formatLabel(row[0].value), 'shape':'circle','color':couleurs.get(row[1].value,couleur_autres)}
    if idname in pics.keys():
        node.update({'label':row[0].value,'shape':'circularImage','image':'images/'+pics[idname],'borderWidth':8,'size':50, 'font':{'color':'#000'}})
    personnes[row[0].value] = node
    id += 1

for i,row in enumerate(wsMouv.rows):
    if i<2:
        continue
    idname = getId(row[0].value)
    node = {'id':id, 'label':formatLabel(row[0].value), 'shape':'circle','color':couleurs.get(row[1].value,couleur_autres),'widthConstraint':{'minimum':150}}
    if idname in pics.keys():
        node.update({'label':row[0].value,'shape':'circularImage','image':'images/'+pics[idname],'borderWidth':8,'size':75, 'font':{'color':'#000'}})
    mouvements[row[0].value] = node
    id += 1

nodes = dict(personnes)
nodes.update(mouvements)

for i,row in enumerate(wsLien.rows):
    if i<2:
        continue

    if row[0].value in nodes.keys() and row[1].value in nodes.keys():
        liens.append({'from':nodes[row[0].value]['id'],'to':nodes[row[1].value]['id'],'label':row[2].value or ""})



import json
nodes = json.dumps(personnes.values()+mouvements.values())
#liens = []
#liens = liens + [ {'from':personnes[l['from']]['id'], 'to':personnes[l['to']]['id'],'label':l['label']} for l in ppliens]
edges = json.dumps(liens)


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

open('reseau.html','w').write(env.get_template('reseautempl.html').render(nodes=nodes,edges=edges).encode('utf-8'))
