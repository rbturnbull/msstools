import xml.etree.ElementTree as ET
from pathlib import Path

def csv_to_tei(input_csv:Path, output_xml:Path, dates:Path|None=None, max_readings:int=0):
    root = ET.Element('TEI', xmlns="http://www.tei-c.org/ns/1.0")
    teiHeader = ET.SubElement(root, 'teiHeader')
    fileDesc = ET.SubElement(teiHeader, 'fileDesc')
    titleStmt = ET.SubElement(fileDesc, 'titleStmt')
    respStmt = ET.SubElement(titleStmt, 'respStmt')
    resp = ET.SubElement(respStmt, 'resp')
    resp.text = "Collated using msstools"

    publicationStmt = ET.SubElement(fileDesc, 'publicationStmt')
    ET.SubElement(publicationStmt, 'p').text = "Not for distribution."

    sourceDesc = ET.SubElement(fileDesc, 'sourceDesc')
    ET.SubElement(sourceDesc, 'p').text = f"Derived from `{input_csv.name}`"

    listWit = ET.SubElement(sourceDesc, 'listWit')

    body = ET.SubElement(root, 'body')

    all_witnesses = set()
    import csv
    with open(input_csv) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            location = row[0]
            if not location:
                continue
            app = ET.SubElement(body, 'app')
            for reading_index, witnesses_for_reading in enumerate(row[1:]):
                if max_readings and reading_index >= max_readings:
                    break
                
                if witnesses_for_reading:
                    rdg = ET.SubElement(app, 'rdg', wit=witnesses_for_reading)
                    rdg.text = str(reading_index)
                    all_witnesses.update(witnesses_for_reading.strip().split())


    if dates:
        dates_dict = {}
        with open(dates) as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                siglum = row[0]
                start = str(int(row[1]))
                end = str(int(row[2]))
                dates_dict[siglum] = (start, end)

    all_witnesses = sorted(all_witnesses)
    for siglum in all_witnesses:
        witness = ET.SubElement(listWit, 'witness', n=siglum)
        if dates:
            start, end = None, None
            if siglum in dates_dict:
                start, end = dates_dict[siglum]
            elif  siglum.endswith("K") and siglum[:-1] in dates_dict:
                start, end = dates_dict[siglum[:-1]]

            if start is not None:
                if start == end:
                    ET.SubElement(witness, 'origDate', when=start)
                else:
                    ET.SubElement(witness, 'origDate', notBefore=start, notAfter=end)
            else:
                print(f"Witness {siglum} not in dates")
        
    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    tree.write(output_xml, encoding="utf-8")