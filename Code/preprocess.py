import xml.etree.ElementTree as ET
from yattag import indent
import inflection as inf
import os
import sys

for arg in sys.argv:
    if arg == "-p":
        index = sys.argv.index(arg)
        nameFile = sys.argv[index+1]
    else:
        continue

tree = ET.parse(nameFile) # Give this file as an argument

root = tree.getroot()

rootAttr = root.attrib

def getSystems(root):
    for elem in root:
        if elem.tag == "Systems":
            for e in elem:
                etiqueta = inf.singularize(e.tag)
                for types in e:
                    if 'Type' in types.tag:
                        text = types.text
                        elem.remove(e)
                        system = ET.SubElement(elem, 'System')
                        system.set('Name', etiqueta)
                        system.set('Type', text)
        else:
            getSystems(elem)

getSystems(root)

def getCoefficients(root):
    coefficientList = []
    for elem in root:
        if elem.tag == "Formula":
            for e in elem:
                etiquetaFormula = e.tag
                
                for coefficient in e:
                    coefficientList.append([coefficient.tag,coefficient.text])
                
                elem.remove(e)
                elem.set('Name', etiquetaFormula)
                coefficients = ET.SubElement(elem, 'Coefficients')
                for coeff in coefficientList:
                    if 'Parameter' not in coeff[0]:
                        coefficient = ET.SubElement(coefficients, 'Coefficient')
                        coefficient.set('Name', coeff[0])
                        value = ET.SubElement(coefficient, 'Value')
                        value.text = coeff[1]
                    else:
                        parameter = ET.SubElement(coefficients, 'Parameter')
                        parameter.set('Name', coeff[0])
                        value = ET.SubElement(parameter, 'Value')
                        value.text = coeff[1]
        else:
            getCoefficients(elem)
getCoefficients(root)

def getSpaces(root):
    for elem in root:
        if elem.tag == "Spaces":
            attributes = elem.attrib
            spacesList = []
            for e in elem: # Space in Spaces
                e.set('SpacesID', attributes['ID'])
                e.set('SpacesIfcGuid', attributes['IfcGuid'])
                spacesList.append(e)
                childList = []
            for child in root.iter():
                childList.append(child.tag)
            if "FinalSpaces" not in childList:
                finalSpaces = ET.SubElement(root, "FinalSpaces")
                for e in spacesList:
                    finalSpaces.append(e)
                
            else:
                for data in root:
                    if data.tag == "FinalSpaces":
                        for e in spacesList:
                            data.append(e)
            
        else:
            getSpaces(elem)
    
    
    elements = root.findall("Spaces")
    for element in elements:
        root.remove(element)
    finalSpaces = root.findall("FinalSpaces")
    for element in finalSpaces:
        element.tag = "Spaces"

getSpaces(root)

def getBehaviorsID(root):
    for elem in root:
        if elem.tag == "Occupant":
            for e in elem: # BehaviorID in Occupant
                elem.set('BehaviorID', e.text)
                elem.remove(e)
        else:
            getBehaviorsID(elem)
getBehaviorsID(root)


def getConcationIfc(root):
    ifcBuilding = ''
    for elem in root:
        if elem.tag == "Building":
            attrList = elem.attrib
            ifcBuilding = attrList['IfcGuid']
            makeConcatenation(elem, ifcBuilding)

        else:
            getConcationIfc(elem)

        
def makeConcatenation(root, ifcBuilding):
    for elem in root:
        if elem.tag == "Space":
            attrList = elem.attrib
            ifcSpace = attrList['IfcGuid']
            ifcZone = attrList['SpacesIfcGuid']
            zone = attrList['SpacesID']
            IfcConcatenation = ifcBuilding + "_" + ifcZone + "_" + ifcSpace
            elem.set('IfcConcatenationZone', ifcBuilding + "_" + ifcZone + "_" + zone)
            elem.set('IfcConcatenation', IfcConcatenation)
        
        else:
            makeConcatenation(elem, ifcBuilding)


getConcationIfc(root)

def getSystems2(root):
    for elem in root:
        if elem.tag == "Space":
            attrList = elem.attrib
            concatenation = attrList['IfcConcatenation']
            for e in elem:
                if e.tag == "Systems":
                    for i in e:
                        if i.tag == "System":
                            attrList2 = i.attrib
                            name = attrList2['Name']
                            i.set('Concatenation', concatenation + "-" + name)
        else:
            getSystems2(elem)
getSystems2(root)


def getBehavior(root):
    for elem in root:
        if elem.tag == "Behavior":
            attrList = elem.attrib
            id = attrList['ID']
            getInteraction(elem, id)
        else:
            getBehavior(elem)

def getInteraction(root, id):
    for elem in root:
        if elem.tag == "Interaction":
            for e in elem:
                if e.tag == "Type":
                    interactionType = e.text
                    elem.set('TypeConcat', id + "-" + interactionType)
                elif e.tag == "Formula":
                    dataList = e.attrib
                    e.set('ConcatForm', id + "-" + dataList['Name'])
                    for coeffs in e:
                        if coeffs.tag == "Coefficients":
                            for coeff in coeffs:
                                if coeff.tag == "Coefficient":
                                    coeffList = coeff.attrib
                                    coeff.set('ConcatName', id + "-" + dataList['Name'] + "-" + coeffList['Name'])
                                elif coeff.tag == "Parameter":
                                    coeffList = coeff.attrib
                                    coeff.set('ConcatName', id + "-" + dataList['Name'] + "-" + coeffList['Name'])
        else:
            getInteraction(elem, id)

getBehavior(root)


def goBeyondOc(root, beyondList):
    for elem in root:
        if elem.tag == "Systems":
            for el in elem:
                if el.tag == "System":
                    attrList = el.attrib
                    if 'Concatenation' in attrList:
                        diffList = attrList['Concatenation'].split('_')
                        beyondList.append(diffList[0] + '_' + diffList[1])

        elif elem.tag == "OccupantID":
            beyondList.append(elem.text)
        
        else:
            goBeyondOc(elem, beyondList)

beyondList = []
goBeyondOc(root, beyondList)
N = 2
beyondList = [beyondList[n:n+N] for n in range(0, len(beyondList), N)]


def getBehaviorIDList(root, beyondList):
    for elem in root:
        if elem.tag == "Occupant":
            attrList = elem.attrib
            for concept in beyondList:
                if concept[1] == attrList['ID']:
                    concept.append(attrList['BehaviorID'])
        
        else:
            getBehaviorIDList(elem, beyondList)

getBehaviorIDList(root, beyondList)

def giveConcat(root, beyondList):
    for elem in root:
        if elem.tag == "Behavior":
            attrList = elem.attrib
            for concept in beyondList:
                if concept[2] == attrList['ID']:
                    elem.set('Concatenation', concept[0])
                    for el in elem:
                        if el.tag == "Needs":
                            for a in el:
                                if a.tag == "Physical":
                                    for b in a:
                                        if b.tag != "ParameterRange":
                                            name = b.tag
                                            a.remove(b)
                                            for c in b:
                                                if c == "ParameterRange":
                                                    a.append(c)
                                                    a.set('Type', concept[0].split('-')[0] + '-' + name + "Need")
                                                    a.set('Name', name + "Need")
                                                else:
                                                    for d in c:
                                                        a.append(d)
                                                        a.set('Type', concept[0].split('-')[0] + '-' + name + "Need")
                                                        a.set('Name', name + "Need")
                                        else:
                                            for c in b:
                                                a.append(c)
                                                a.set('Type', concept[0].split('-')[0] + '-' + "Need")
                                                a.set('Name', "Need")
        
        else:
            giveConcat(elem, beyondList)

giveConcat(root, beyondList)

def changeIfcName(root):
    for elem in root:
        if elem.tag == 'Building':
            attrList = elem.attrib
            ifcBuilding = attrList['IfcGuid']
            del elem.attrib["IfcGuid"]
            elem.set('BuildingIfcGuid', ifcBuilding)
        else:
            changeIfcName(elem)
changeIfcName(root)


mydata = ET.tostring(root, encoding='utf-8').decode()
pretty_string = indent(mydata)
nameFile = nameFile.split('/')
nameFile.pop()
nameFile.append('out.xml')
nameFile = '/'.join(nameFile)
myfile = open(nameFile, "w")
myfile.write(pretty_string)
myfile.close()


nameFile

os.system('java -jar xml2json.jar -p ' + nameFile)