# About make_specdata1.py

As of: 2020-12-18

This script reads an IPTC NewsML-G2 XML schema file in the /xmlschema folder and generates these files in the ./output folder:

* make_specdata1_log.txt: a text file logging which data were retrieved from the XML schema.
* ng2-elemattrib-matrix.csv: all XML elements specified by NewsML-G2 have also a set of attributes. A table serialized by this CSV file has a row for each XML element and a column for each attribute used by any element. The cell of an element and an attribute tells if the attribute is specified for the element:
    * value '.' : use is not specified
    * value 'o' : use of the attribute is optional
    * value 'r' : use of the attribute is required
    * value '?' : attribute can be used, but neither 'required' nor 'optional' is specified.
    
* ng2-specdata1_of-schema_{schema filename}.json: a JSON object, each XML element is a property at the top level with an object as value. Each element object reflects:
    * The XML schema name of the property. Be aware that the XML Schema may specify multiple elements with the same name. In this case the first occurrence has the XML element name as property name, all other occurrences got a '_{number}' appended.
    * A property named 'attributes'. Its value is an object reflecting all attributes specified for this element. The object property name is the XML attribute name, its value is a sequence of the data type and the cardinality of the attribute, separated by a |. The value 'NA' indicates that a data type or cardinality of this attribute is not available in the XML schema file.
    * A property named 'childelements'. (New on 2020-12-18) Its value is a string of NewsML-G2 element names in the defined sequence, separated by '|'s. A "defined sequence" reflects the order of element definitions in the XML schema. It ignores if the context xs:sequence or xs:choice applies, therefore it works well for building a NewsML-G2 document but not for validity checking.    
    
## How to use

* The 'constant values' region at the top of the script provides the file path for output files - as explained above. This file path can be changed to another target folder and the filename may be changed.
* The 'constant values' region includes the constant XMLSCHEMAFN: this is the file name of the NewsML-G2 XML schema in the /xmlschema folder to be processed by this script. The to-be-processed schema file must be copied to this folder by the user. (The NewsML-G2 2.29 XML schema file is provided as example by this repository.)  
* The 'constant values' region includes the constant CSVSEP: this is a single character acting as separator of any CSV file. May be adjusted to the local culture.
* As result of executing this script the files in the /output folder mentioned above should be created.

## TO-DOs

These additional features are planned:
* Providing information about the ancestor(s) of an element. This helps to identify in which context each element of elements with multiple occurrence is specified.

    