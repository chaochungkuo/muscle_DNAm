import csv
import os

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_root = os.path.join(repo_root, "output")
output_dir = os.path.join(repo_root, "output", "GEO_upload")

input_files = [
    os.path.join(output_root, "processed_bVals.csv"),
    os.path.join(output_root, "processed_mVals.csv"),
]

os.makedirs(output_dir, exist_ok=True)

# Conversion table
conversion = {
    "ALS.118083": "ALS.1",
    "ALS.118949": "ALS.2",
    "ALS.130992": "ALS.3",
    "ALS.136333": "ALS.4",
    "ALS.144074": "ALS.5",
    "ALS.148766": "ALS.6",
    "IBM.B2017.25291": "IBM.1",
    "IBM.B2017.34805": "IBM.2",
    "IBM.B2018.35271": "IBM.3",
    "IBM.B2016.2782": "IBM.4",
    "IBM.B2016.4913": "IBM.5",
    "IBM.B2018.20413": "IBM.6",
    "IBM.B2018.7235": "IBM.7",
    "IBM.126074": "IBM.8",
    "IBM.127732": "IBM.9",
    "IBM.129720": "IBM.10",
    "IBM.135065": "IBM.11",
    "IBM.135973": "IBM.12",
    "IBM.137130": "IBM.13",
    "IBM.140367": "IBM.14",
    "IBM.128987": "IBM.15",
    "IBM.118369": "IBM.16",
    "NMA.120001": "NMA.1",
    "NMA.120314": "NMA.2",
    "NMA.128823": "NMA.3",
    "NMA.122362": "NMA.4",
    "NMA.134504": "NMA.5",
    "NMA.138501": "NMA.6",
    "NMA.138899": "NMA.7",
    "NMA.148513": "NMA.8",
    "NMA.148831": "NMA.9",
    "NMA.145548": "NMA.10",
    "NMA.147235": "NMA.11",
    "NMA.148456": "NMA.12",
    "NMA.149314": "NMA.13",
    "PM.B2016.8281": "PM.1",
    "PM.B2016.43523": "PM.2",
    "PM.B2017.7816": "PM.3",
    "PM.B2018.30787": "PM.4.1",
    "PM.B2018.30786_Mm": "PM.4.2",
    "PM.B2018.30786_Leu": "PM.4.3",
    "Control.MalicotFP7": "Control.1",
    "Control.MalicotDP4": "Control.2",
    "Control.MalicotLP1": "Control.3",
    "Control.MalicotHR9": "Control.4",
    "Control.MalicotQH5": "Control.5",
    "Control.MalicotKB5": "Control.6",
    "Control.MalicotYB2": "Control.7",
    "Control.MalicotGA5": "Control.8",
    "Control.MalicotGI3": "Control.9",
    "Control.MalicotVO8": "Control.10",
    "Control.MalicotCC7": "Control.11",
    "Control.MalicotPN8": "Control.12",
    "Control.MalicotGY6": "Control.13",
    "Control.MalicotEJ9": "Control.14",
    "Control.MalicotBK1": "Control.15",
    "Control.MalicotRP9": "Control.16",
    "Control.MalicotIF3": "Control.17",
    "Control.MalicotWL2": "Control.18",
    "Control.MalicotBI5": "Control.19",
    "Control.MalicotGM5": "Control.20",
    "Control.MalicotYQ2": "Control.21",
    "Control.MalicotSF6": "Control.22",
    "Control.MalicotQP4": "Control.23",
    "Control.MalicotBW3": "Control.24",
}

for infile in input_files:
    outfile = os.path.join(output_dir, os.path.basename(infile))

    with open(infile, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    header = rows[0]
    new_header = [conversion.get(col, col) for col in header]
    rows[0] = new_header

    with open(outfile, "w", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(rows)

    print(f"Written: {outfile}")
