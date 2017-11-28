def sort_xml_attributes(elem):
    """
    Order the attributes of XML elements in an Elementree. Useful when diffing
    two XML strings.
    """
    for child in elem.iterchildren():
        if child.attrib:
            ordered_attrib = sorted(child.attrib.items())
            child.attrib.clear()
            for key, value in ordered_attrib:
                child.attrib[key] = value

        sort_xml_attributes(child)
