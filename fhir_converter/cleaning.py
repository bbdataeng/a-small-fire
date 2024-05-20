import pandas as pd
import argparse

"""Dataset Cleaning"""

parser = argparse.ArgumentParser(description="Data Cleaning")
parser.add_argument("input_file", type=str, help="File di Input")
args = parser.parse_args()

input_file = args.input_file
print(input_file)


data = pd.read_excel(input_file)

data = data.rename(columns=lambda x: x.strip())

# explode SAMPLE_PRESERVATION_MODE in more rows
data["SAMPLE_PRESERVATION_MODE"] = data["SAMPLE_PRESERVATION_MODE"].str.split("_")
data = data.explode("SAMPLE_PRESERVATION_MODE")
data["SAMPLE_PRESERVATION_MODE"] = data["SAMPLE_PRESERVATION_MODE"].apply(
    lambda x: x[0] if isinstance(x, list) else x
)

# map to its storage temperature
map_storagetemp = {
    "FFPE": "RT",
    "SNAP FROZEN": "-80",
    "BLOOD": "-80",
    "CELL": "-80",
    "SNAP": "-80",
    "FROZEN": "-80",
    "FRESH FROZEN": "-80",
    "OCT": "-80",
}
data["STORAGE_TEMPERATURE"] = data["SAMPLE_PRESERVATION_MODE"].map(map_storagetemp)

# clean ICD10
data["ICD-10"] = data["ICD-10"].str.replace(",", "")
data["ICD-10"] = data["ICD-10"].str.replace(".", "")

def add_point(icd):
    icd = str(icd)
    if "." not in icd: 
        icd = icd[:3] + "." + icd[3:]
        return icd

data["ICD-10"] = data["ICD-10"].apply(add_point)



# check for empty columns
# data.dropna(inplace=True)

# clean patient id
# data['PATIENT_ID'] = data['PATIENT_ID'].str.replace("BBIRE-T", "")


# save file
output_file = input_file.split(".")[-2]
print(f"{data.shape[0]} samples nel file {output_file}.")
data.to_excel(f"{output_file}_clean.xlsx", index=False)
