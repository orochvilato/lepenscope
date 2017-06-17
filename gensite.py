# -*- coding: utf-8 -*-
import requests
import json
import jinja2
import os

candidats = []
import requests
response = requests.get('https://docs.google.com/spreadsheets/d/1FFz6SUbp1NzpijHxYXBqMkOdjpui6V5fPP5wp4C7CBU/export?format=csv&id=1FFz6SUbp1NzpijHxYXBqMkOdjpui6V5fPP5wp4C7CBU&gid=0')
import csv
from cStringIO import StringIO
f = StringIO(response.content)
reader = csv.reader(f,delimiter=',',quotechar='"')
categories = {}
personnes = {}
liens = []
ppliens = []
id = 1
for i,row in enumerate(reader):
    if i<2:
        continue
    if not row[0] in categories.keys():
        s = row[0].split(' ')
        label = s[0] + '\n' + ' '.join(s[1:])
        categories[row[0]] = {'id':id, 'label':label, 'shape':'box'}
        catid = id
        id += 1
    else:
        catid = categories[row[0]]['id']
    if not row[1] in personnes.keys():
        s = row[1].split(' ')
        label = s[0] + '\n' + ' '.join(s[1:])

        personnes[row[1]] = {'id':id, 'label':label, 'shape':'circle'}
        persid = id
        id += 1
    else:
        persid = personnes[row[1]]['id']
    liens.append({'from':persid,'to':catid})
    print row
    print {'from':persid,'to':catid}
    if row[10]:
        pl = row[10].split('\n')
        pldesc = row[11].split('\n')

        for i in range(len(pl)):
            if not pl[i] in personnes.keys():
                s = pl[i].split(' ')
                label = s[0] + '\n' + ' '.join(s[1:])
                personnes[pl[i]] = {'id':id, 'label':label,'shape':'circle'}
                id += 1

            ppliens.append({'from':row[1],'to':pl[i],'label':pldesc[i]})



import json
nodes = json.dumps(categories.values() + personnes.values())

liens = liens + [ {'from':personnes[l['from']]['id'], 'to':personnes[l['to']]['id'],'label':l['label']} for l in ppliens]
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
