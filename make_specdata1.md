# About make_specdata1.py

This script reads an IPTC NewsML-G2 XML schema file and generates these files in the ./output folder:

* make_specdata1_log.txt: a text file logging which data were retrieved from the XML schema.
* ng2-elemattrib-matrix.csv: all XML elements specified by NewsML-G2 have also a set of attributes. A table serialized by this CSV file has a row for each XML element and a column for each attribute used by any element. The cell of an element and an attribute tells if the attribute is specified for the element:
    * value '.' : use is not specified
    * value 'o' : use of the attribute is optional
    * value 'r' : use of the attribute is required
    * value '?' : attribute can be used, but neither 'required' nor 'optional' is specified.
    
* ng2-specdata1_of-schema_{schema filename}.json: a JSON object, each XML element is a property at the top level with an object as value. Each element object reflects:
    * the XML schema name of the property. Be aware that the XML Schema may specify multiple elements with the same name. In this case the first occurrence has the XML element name as property name, all other occurrences got a '_{number}' appended.
    * a property named 'attributes'. Its value is an object reflecting all attributes specified for this element. The object property name is the XML attribute name, its value is a sequence of the data type and the cardinality of the attribute, separated by a |.
    
## TO-DOs

These additional features are planned:
* Providing information about the ancestor(s) of an element. This helps to identify in which context each element of elements with multiple occurrence is specified.

    