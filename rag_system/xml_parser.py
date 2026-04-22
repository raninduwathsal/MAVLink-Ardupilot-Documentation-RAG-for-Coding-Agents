import xml.etree.ElementTree as ET
import json
import os

def parse_mavlink_xml(file_path):
    """
    Parses a MAVLink XML message definition file and returns a list of structured text blocks.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML {file_path}: {e}")
        return []

    parsed_blocks = []
    
    # Process Enums
    for enum in root.findall(".//enum"):
        enum_name = enum.get("name")
        enum_description = ""
        desc_elem = enum.find("description")
        if desc_elem is not None:
            enum_description = desc_elem.text.strip() if desc_elem.text else ""
            
        enum_text = f"MAVLink Enum: {enum_name}\nDescription: {enum_description}\nValues:\n"
        
        for entry in enum.findall("entry"):
            val = entry.get("value")
            name = entry.get("name")
            desc = ""
            d_elem = entry.find("description")
            if d_elem is not None:
                desc = d_elem.text.strip() if d_elem.text else ""
            enum_text += f"- {name} ({val}): {desc}\n"
        
        parsed_blocks.append({
            "text": enum_text,
            "source": str(file_path),
            "type": "enum",
            "name": enum_name
        })

    # Process Messages
    for msg in root.findall(".//message"):
        msg_name = msg.get("name")
        msg_id = msg.get("id")
        msg_description = ""
        desc_elem = msg.find("description")
        if desc_elem is not None:
            msg_description = desc_elem.text.strip() if desc_elem.text else ""
            
        msg_text = f"MAVLink Message: {msg_name} (ID: {msg_id})\nDescription: {msg_description}\nFields:\n"
        
        for field in msg.findall("field"):
            f_name = field.get("name")
            f_type = field.get("type")
            f_desc = field.text.strip() if field.text else ""
            msg_text += f"- {f_name} ({f_type}): {f_desc}\n"
            
        parsed_blocks.append({
            "text": msg_text,
            "source": str(file_path),
            "type": "message",
            "name": msg_name
        })
        
    return parsed_blocks
