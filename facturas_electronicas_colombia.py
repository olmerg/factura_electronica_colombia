"""Script to read all the xml of zips with Colombian Electronics bills
by @olmerg
LICENSE:BSD
2024
Returns:
    csv: list of metadata of the bills.
"""
import glob
import csv
from zipfile import ZipFile
from xml.dom import minidom


FIELDS ={
    'vendedor':['cac:SenderParty','cac:PartyTaxScheme','cbc:RegistrationName'],
    'vendedor.nit':['cac:SenderParty','cac:PartyTaxScheme','cbc:CompanyID'],
    'comprador': ['cac:ReceiverParty','cac:PartyTaxScheme','cbc:RegistrationName'],
    'comprador.cc':['cac:ReceiverParty','cac:PartyTaxScheme','cbc:CompanyID'],
    'fecha_compra':['cbc:IssueDate'],
}
ATTACHMENT={'precio_total':['cac:LegalMonetaryTotal','cbc:PayableAmount']}

# https://github.com/juanor9/xml-fe-analizer

def get_data(file:minidom.Document,tags:list[str])-> str:
    """Get specific tag text of a minidom.Document.

    Args:
        file (minidom.Document): xml file
        tags (list[str]): list of the tree of tags

    Returns:
        str: data of the last child tag.
    """
    if not tags:
        return ''
    dom=file.getElementsByTagName(tags[0])
    if not dom:
        return ''
    dom = dom[0]
    for tag in tags[1:]:
        dom=dom.getElementsByTagName(tag)
        if not len:
            return ''
        dom = dom[0]
    return dom.firstChild.data

def get_row(xml_data:str)->list:
    """Reads al the tags required

    Args:
        xml_data (str): xml document in string

    Returns:
        list: a list with all the data of the tags.
    """
    row=[]
    xml_file = minidom.parseString(xml_data)
    for value in FIELDS.values():
        row.append(get_data(xml_file,value))
    attachment = get_data(xml_file,['cac:Attachment','cac:ExternalReference','cbc:Description'])
    try:
        attachment= minidom.parseString(attachment)
        for value in ATTACHMENT.values():
            row.append(get_data(attachment,value))
    except Exception:
        for _ in ATTACHMENT:
            row.append(None)
    return row

if __name__ == '__main__':
    # TODO: add folder dir and output file input parameters.
    list_bills=[['zip_file','xml_file']+list(FIELDS)+list(ATTACHMENT)]
    zip_files = glob.glob("*.zip")
    for zip_name in zip_files:
        archive = ZipFile(zip_name, 'r')
        files = archive.namelist()
        files = [name for name in archive.namelist() if name.endswith('.xml')]
        for xml_name in files:
            data = archive.read(xml_name).decode()
            list_bills.append([zip_name, xml_name]+get_row(data))
    csv_name = 'bills.csv'
    with open(csv_name, 'w', newline="", encoding='utf-8') as csv_file:
        csvwriter = csv.writer(csv_file)
        for bill in list_bills:
            csvwriter.writerow(bill)
