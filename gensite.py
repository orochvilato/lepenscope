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
            pics[id[0].encode('utf8')] = image['name']
        else:
            pics[id[1].encode('utf8')] = image['name']
        if image['name'] in loadedimages:
            continue
        r = requests.get('https://drive.google.com/uc?id='+image['id']+'&export=download')


        open('images/%s' % image['name'],'w').write(r.content)

loadImages()
candidats = []
import requests
response = requests.get('https://docs.google.com/spreadsheets/d/1FFz6SUbp1NzpijHxYXBqMkOdjpui6V5fPP5wp4C7CBU/export?format=csv&id=1FFz6SUbp1NzpijHxYXBqMkOdjpui6V5fPP5wp4C7CBU&gid=0')
import csv
from cStringIO import StringIO
f = StringIO(response.content)
reader = csv.reader(f,delimiter=',',quotechar='"')
couleurs = {
    'Souverainiste':'#374682',
    'Identitaire':'#915537',
    'Catholique intégriste': '#913773'
}
couleur_autres = '#414141'
personnes = {}
liens = []
ppliens = []
id = 1
doublons = {}

for i,row in enumerate(reader):
    if i<2:
        continue

    if 1: #not row[1] in personnes.keys():
        s = row[1].split(' ')
        label = s[0] + '\n' + ' '.join(s[1:])
        label = '\n'.join(s)
        idname = row[0].lower().replace('-','').replace(' ','')
        node = {'id':id, 'label':label, 'shape':'circle','color':couleurs.get(row[0],couleur_autres)}
        if idname in pics.keys():
            node.update({'shape':'circularImage','image':'images/'+pics[idname]})
        personnes[row[1]] = node

        persid = id
        id += 1
    else:
        persid = personnes[row[1]]['id']

    if row[10]:
        pl = row[10].split('\n')
        pldesc = row[11].split('\n')
        for i in range(len(pl)):
            if not pl[i] in personnes.keys():
                s = pl[i].split(' ')
                label = s[0] + '\n' + ' '.join(s[1:])
                label = '\n'.join(s)
                idname = row[0].lower().replace('-','').replace(' ','')
                node = {'id':id,
                                    'label':label,
                                    'shape':'circle',
                                    'color':couleur_autres,
                                    'widthConstraint': {'minimum': 150 }
                                    }
                if idname in pics.keys():
                    node.update({'shape':'circularImage','image':'images/'+pics[idname]})
                personnes[pl[i]] = node
                id += 1

            if (pl[i],row[1]) in doublons.keys():
                oldlabel = ppliens[doublons[(pl[i],row[1])]]['label']
                if oldlabel:
                    ppliens[doublons[(pl[i],row[1])]]['label'] += ' / '
                ppliens[doublons[(pl[i],row[1])]]['label'] += pldesc[i] if i<len(pldesc) else ""
            else:
                doublons[(row[1],pl[i])] = len(ppliens)
                ppliens.append({'from':row[1],'to':pl[i],'label':pldesc[i] if i<len(pldesc) else ""})





import json
nodes = json.dumps(personnes.values())

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
