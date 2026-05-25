import os
import zipfile
import xml.etree.ElementTree as ET

def extract_text_from_pptx(file_path):
    text_content = []
    try:
        with zipfile.ZipFile(file_path, 'r') as z:
            for item in z.namelist():
                if item.startswith('ppt/slides/slide') and item.endswith('.xml'):
                    xml_content = z.read(item)
                    root = ET.fromstring(xml_content)
                    for elem in root.iter():
                        if elem.tag.endswith('}t'):
                            if elem.text:
                                text_content.append(elem.text)
        return '\n'.join(text_content)
    except Exception as e:
        return str(e)

def extract_text_from_xlsx(file_path):
    text_content = []
    try:
        with zipfile.ZipFile(file_path, 'r') as z:
            # Read shared strings if any
            shared_strings = []
            if 'xl/sharedStrings.xml' in z.namelist():
                xml_content = z.read('xl/sharedStrings.xml')
                root = ET.fromstring(xml_content)
                for elem in root.iter():
                    if elem.tag.endswith('}t'):
                        if elem.text:
                            shared_strings.append(elem.text)
            
            for item in z.namelist():
                if item.startswith('xl/worksheets/sheet') and item.endswith('.xml'):
                    xml_content = z.read(item)
                    root = ET.fromstring(xml_content)
                    for elem in root.iter():
                        if elem.tag.endswith('}v'):
                            # Wait, 'v' is value. Sometimes it's an index to shared strings.
                            # Just grab all text from shared strings as that represents the text in the file.
                            pass
            return '\n'.join(shared_strings)
    except Exception as e:
        return str(e)

import sys
sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"c:\Users\User\Downloads\DetoxProgram\언블리버블 v2"

print("--- PPTX ---")
pptx_path = os.path.join(base_dir, "프로젝트PPT.pptx")
print(extract_text_from_pptx(pptx_path)[:2000])

print("\n--- XLSX: 요구사항정의서 ---")
req_path = os.path.join(base_dir, "01. 요구정의", "요구사항정의서.xlsx")
print(extract_text_from_xlsx(req_path)[:2000])

print("\n--- XLSX: 기능 정의서 ---")
func_path = os.path.join(base_dir, "02. 분석", "기능 분석 - 기능 정의서.xlsx")
print(extract_text_from_xlsx(func_path)[:2000])

