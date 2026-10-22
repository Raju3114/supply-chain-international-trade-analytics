"""
package_pbit.py
---------------
Packages the Tabular Semantic Model and Report Layout into a standard
Power BI Template (.pbit) and Power BI Report (.pbix) archive that opens directly
in Power BI Desktop.

Author: Antigravity & Senior Data Analyst Mentor
"""

import os
import json
import zipfile

OUTPUT_PBIT = os.path.join("power_bi", "reports", "Supply_Chain_Analytics.pbit")
OUTPUT_PBIX = os.path.join("power_bi", "reports", "Supply_Chain_Analytics.pbix")
MODEL_BIM = os.path.join("power_bi", "Supply_Chain_Analytics.SemanticModel", "model.bim")
REPORT_JSON = os.path.join("power_bi", "Supply_Chain_Analytics.Report", "report.json")

CONTENT_TYPES_XML = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json" />
  <Default Extension="xml" ContentType="application/xml" />
  <Override PartName="/DataModelSchema" ContentType="application/json" />
  <Override PartName="/Report/Layout" ContentType="application/json" />
  <Override PartName="/Settings" ContentType="application/json" />
  <Override PartName="/Version" ContentType="text/plain" />
</Types>"""

def create_pbit():
    os.makedirs(os.path.join("power_bi", "reports"), exist_ok=True)
    
    with open(MODEL_BIM, "r", encoding="utf-8") as f:
        model_data = json.load(f)
    
    with open(REPORT_JSON, "r", encoding="utf-8") as f:
        report_data = json.load(f)

    # Encode components in UTF-16LE as required by Power BI binary specification
    model_bytes = json.dumps(model_data).encode("utf-16le")
    report_bytes = json.dumps(report_data).encode("utf-16le")
    settings_bytes = json.dumps({"version": "1.0"}).encode("utf-16le")
    version_bytes = "1.28".encode("utf-8")
    content_types_bytes = CONTENT_TYPES_XML.encode("utf-8")

    for target_path in [OUTPUT_PBIT, OUTPUT_PBIX]:
        print(f"Creating Power BI package: {target_path}...")
        with zipfile.ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", content_types_bytes)
            zf.writestr("Version", version_bytes)
            zf.writestr("Settings", settings_bytes)
            zf.writestr("DataModelSchema", model_bytes)
            zf.writestr("Report/Layout", report_bytes)
        
        file_size_kb = os.path.getsize(target_path) / 1024
        print(f"  -> Generated {target_path} ({file_size_kb:.2f} KB)")

if __name__ == "__main__":
    create_pbit()
