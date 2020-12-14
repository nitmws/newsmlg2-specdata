"""
    Script for retrieving information from an IPTC NewsML-G2 XML Schema
    and creating documents with data reflecting the specification of
    XML elements and their attributes, child elements and more
"""

from xml.etree import ElementTree as ET
import json

# constant values
LOGFP = './output/make_specdata1_log.txt'
MATRIXFP = './output/ng2-elemattrib-matrix.csv'
SPECDATA1FN = './output/ng2-specdata1_of-schema_'
CSVSEP = ';'

NS = {
        "xs": "http://www.w3.org/2001/XMLSchema",
        "nar": "http://iptc.org/std/nar/2006-10-01/",
        "iptc-x": "http://iptc.org/std/nar/schemaextensions/"
    }

"""
    ***************************************************************************
    Helper functions
"""

def logfile_setup():
    logfile = open(LOGFP, 'w')
    logfile.close()


def logfile_addline(textline):
    logfile = open(LOGFP, 'a')
    logfile.write(textline + '\n')
    logfile.close()


def matrixfile_setup():
    matrixfile = open(MATRIXFP, 'w')
    matrixfile.close()


def matrixfile_addline(textline):
    matrixfile = open(MATRIXFP, 'a')
    matrixfile.write(textline + '\n')
    matrixfile.close()


def copy_withoutkeys(d, wokeys):
    return {x: d[x] for x in d if x not in wokeys}

def get_attributedata(testnode):
    attrdata = {}
    for xsattr in testnode.findall('.//xs:attribute[@name]', NS):
        attrvaluestr = ''
        if 'type' in xsattr.attrib:
            attrvaluestr += xsattr.attrib['type']
        else:
            attrvaluestr += 'NA'
        if 'use' in xsattr.attrib:
            attrvaluestr += '|' + xsattr.attrib['use']
        else:
            attrvaluestr += '|NA'
        attrdata[xsattr.attrib['name']] = attrvaluestr
    return attrdata

def complextypes_childelemnames(xsroot):
    ng2cplxtypes = {}
    for xscplxtype in xsroot.findall('.//xs:complexType[@name]', NS):
        childelemnames = []
        for childelem in xscplxtype.findall('.//xs:element', NS):
            if 'name' in childelem.attrib:
                childelemnames.append(childelem.attrib['name'])
            if 'ref' in childelem.attrib:
                childelemnames.append(childelem.attrib['ref'])
        ng2cplxtypes[xscplxtype.attrib['name']] = childelemnames
    return ng2cplxtypes

def get_allchildelems(xsroot, parentnode):
    # prerequisite: the lists of child elements in a complex type
    ng2cplxtypedata = complextypes_childelemnames(xsroot)
    childelemnames = []
    # check for child elements of base type
    for xsextension in parentnode.findall('.//xs:extension', NS):
        if 'base' in xsextension.attrib:
            basetypename = xsextension.attrib['base']
            if basetypename in ng2cplxtypedata:
                for childelemname in ng2cplxtypedata[basetypename]:
                    childelemnames.append(childelemname)

    # check for inline child elements
    for childelem in parentnode.findall('.//xs:element', NS):
        if 'name' in childelem.attrib:
            childelemnames.append(childelem.attrib['name'])
        if 'ref' in childelem.attrib:
            childelemnames.append(childelem.attrib['ref'])

    return childelemnames


def process_ng2_schema(xmlschema_filename):

    xstree = ET.parse('./xmlschema/' + xmlschema_filename)
    xsroot = xstree.getroot()

    # ***** generate an attribute-dictionary for each attributeGroup - in a dictionary
    print('*** AttributeGroups')
    logfile_addline('*** AttributeGroups')
    ng2attrgroupsdata = {}
    for xsattrgroup in xsroot.findall('.//xs:attributeGroup[@name]', NS):
        ng2attrgroupsdata[xsattrgroup.attrib['name']] = get_attributedata(xsattrgroup)

    ng2attrgroupnames = list(ng2attrgroupsdata.keys())
    ng2attrgroupnames.sort()
    ctr = 0
    for ng2attrgroupname in ng2attrgroupnames:
        ctr = ctr + 1
        jsonstr = json.dumps(ng2attrgroupsdata[ng2attrgroupname])
        logline = str(ctr) + " " + ng2attrgroupname + ' ' + jsonstr
        print(logline)
        logfile_addline(logline)

    # ***** generate an attribute-dictionary for each complexType - in a dictionary
    print('*** Complex Types')
    logfile_addline('*** Complex Types')
    ng2cplxtypesdata = {}
    for xscplxtype in xsroot.findall('.//xs:complexType[@name]', NS):
        ng2cplxtypedata = {}
        # check for referenced attributeGroups
        for xsattrgr in xscplxtype.findall('.//xs:attributeGroup[@ref]', NS):
            attrgrname = xsattrgr.attrib['ref']
            if ng2attrgroupsdata[attrgrname]:
                ng2cplxtypedata.update(ng2attrgroupsdata[attrgrname])
        # check for inline attributes
        attrdata = get_attributedata(xscplxtype)
        ng2cplxtypedata.update(attrdata)
        # set the attribute-dict
        ng2cplxtypesdata[xscplxtype.attrib['name']] = ng2cplxtypedata
    # now once again for referenced types
    for xscplxtype in xsroot.findall('.//xs:complexType[@name]', NS):
        ng2cplxtypedata = {}
        # check for extended type
        for xsextension in xscplxtype.findall('.//xs:extension[@base]', NS):
            typename = xsextension.attrib['base']
            if typename in ng2cplxtypesdata:
                ng2cplxtypesdata[xscplxtype.attrib['name']].update(ng2cplxtypesdata[typename])

    ng2cplxtypenames = list(ng2cplxtypesdata.keys())
    ng2cplxtypenames.sort()
    ctr = 0
    for ng2cplxtypename in ng2cplxtypenames:
        ctr = ctr + 1
        jsonstr = json.dumps(ng2cplxtypesdata[ng2cplxtypename])
        logline = str(ctr) + " " + ng2cplxtypename + ' ' + jsonstr
        print(logline)
        logfile_addline(logline)

    # ***** generate an attribute-dictionary for each element - in a dictionary
    #       include all referenced attributeGroups and complextTypes
    print('*** Elements')
    logfile_addline('*** Elements')
    ng2elemsdata = {}
    for xselement in xsroot.findall('.//xs:element[@name]', NS):
        ng2elemattribs = {}  # attribute-dictionary of this element
        ng2elembasename = xselement.attrib['name']
        ng2elemname = ng2elembasename
        extctr = 1
        while ng2elemname in ng2elemsdata:
            extctr += 1
            ng2elemname = ng2elembasename + '_' + str(extctr)

        # check for referenced type
        if 'type' in xselement.attrib:
            typename = xselement.attrib['type']
            if typename in ng2cplxtypesdata:
                ng2elemattribs.update(ng2cplxtypesdata[typename])
        # check for base type extended by this element
        for xsextension in xselement.findall('.//xs:extension[@base]', NS):
            typename = xsextension.attrib['base']
            if typename in ng2cplxtypesdata:
                ng2elemattribs.update(ng2cplxtypesdata[typename])

        # check for referenced attributeGroups
        for xsattrgr in xselement.findall('.//xs:attributeGroup[@ref]', NS):
            attrgrname = xsattrgr.attrib['ref']
            if ng2attrgroupsdata[attrgrname]:
                ng2elemattribs.update(ng2attrgroupsdata[attrgrname])

        # check for inline attributes of this document
        attrdata = get_attributedata(xselement)
        ng2elemattribs.update(attrdata)

        # finally: add the data of this element to the dict
        ng2elemdata = {'name': ng2elembasename}
        ng2elemdata['attributes'] = ng2elemattribs
        ng2elemsdata[ng2elemname] = ng2elemdata

    ng2elemnames = list(ng2elemsdata.keys())
    ng2elemnames.sort()
    ctr = 0
    for ng2elemname in ng2elemnames:
        ctr = ctr + 1
        jsonstr = json.dumps(ng2elemsdata[ng2elemname])
        logline = str(ctr) + " " + ng2elemname + " " + jsonstr
        print(logline)
        logfile_addline(logline)

    return ng2elemsdata


def create_matrix(ng2elemsdata):
    matrixfile_setup()

    allattrnames = []
    for ng2elemname in ng2elemsdata:
        ng2elemattribs = ng2elemsdata[ng2elemname]['attributes']
        for attrname in ng2elemattribs:
            if not(attrname in allattrnames):
                allattrnames.append(attrname)

    allattrnames.sort()
    # create to column header row
    matrixline = 'element_name' + CSVSEP
    for attrname in allattrnames:
        matrixline += attrname + CSVSEP
    matrixfile_addline(matrixline)

    # iterate across the elements
    ng2elemnames = list(ng2elemsdata.keys())
    ng2elemnames.sort()

    for ng2elemname in ng2elemnames:
        ng2elemattribs = ng2elemsdata[ng2elemname]['attributes']
        matrixline = ng2elemname + CSVSEP
        for attrname in allattrnames:
            if attrname in ng2elemattribs:
                attrvaluestr = ng2elemattribs[attrname]
                attrvalues = attrvaluestr.split('|')
                matrixvalue = '$'
                if len(attrvalues) > 1:
                    if attrvalues[1] == 'NA':
                        matrixvalue = '?'
                    else:
                        matrixvalue = attrvalues[1][:1]
                matrixline += matrixvalue + CSVSEP
            else:
                matrixline += '.' + CSVSEP
        matrixfile_addline(matrixline)

def create_specdata_asjson(ng2elemsdata, xmlschema_filename):
    jsonstr = json.dumps(ng2elemsdata, indent=2)
    specdatafp = SPECDATA1FN + xmlschema_filename + '.json'
    elemspecdatafile = open(specdatafp, 'w')
    elemspecdatafile.write(jsonstr)
    elemspecdatafile.close()


"""
    ***************************************************************************
    Main function
"""
logfile_setup()
xmlschemafn = 'NewsML-G2_2.29-spec-All-Power.xsd'
logfile_addline(xmlschemafn)
ng2_specdata1 = process_ng2_schema(xmlschemafn)
create_matrix(ng2_specdata1)
create_specdata_asjson(ng2_specdata1, xmlschemafn)
print('the END')
