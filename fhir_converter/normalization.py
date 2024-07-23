from datetime import date, timedelta, datetime
from typing import Dict, Optional, Union, Any

import input_models as models
from loguru import logger as log

from fhir.resources.fhirtypes import Date
import re
import yaml
# import icd10


class FHIRNormalization:

    # https://www.icd10data.com/search
    @staticmethod
    def get_diagnosis_icd10(
        diag : str
    ) -> str:
        return diag


def apply_map(label: str, value: str, mapping: Dict[str, str]) -> str:
    print("value", value)
    for miabis_value, biobank_values in mapping.items():
        if isinstance(biobank_values, str):
            # if a single string, convert it to a list
            biobank_values = [biobank_values]

        if value in biobank_values:
            return miabis_value

def apply_map_IG(label: str, value: str, mapping: Dict[str, str]) -> str:

    if value not in mapping:
        raise ValueError(f"Invalid value for {label}: {value}")

    return mapping[value]

 
def load_config(config_path: str) -> Dict:
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
    
def normalize_input(patient_data: Dict[str, Any], config_path: str) -> Dict[str, Any]:
    '''Normalize input data based on configuration'''

    

    config = load_config(config_path)
    field_mappings = config.get("field_mappings", {})
    value_mappings = config.get("value_mappings", {})

    # field name mappings
    for miabis_field, biobank_field in field_mappings.items():
        if biobank_field in patient_data:
            patient_data[miabis_field] = patient_data.pop(biobank_field)

    patient_data['STORAGE_TEMPERATURE'] = str(patient_data['STORAGE_TEMPERATURE'])
    # value mappings
    for key, mapping in value_mappings.items():
        print("KEY: ", key)
        print("MAPPING: ", mapping)
        print("patient_data[key]", patient_data[key])
        if key in patient_data:
            patient_data[key] = apply_map(key, patient_data[key], mapping)

    try:
        patient_data['DATE_DIAGNOSIS']
    except: # if there's no diagnosis date, it is equal to year of DOB + AGE_AT_PRIMARY_DIAGNOSIS
        diagnosis_year = patient_data["BIRTH_DATE"].year + patient_data["AGE_AT_PRIMARY_DIAGNOSIS"]
        patient_data['DATE_DIAGNOSIS'] = datetime.strptime(f"{diagnosis_year}-01-01", r"%Y-%m-%d")

    print("patient_data: ", patient_data)

    return patient_data

def normalize_output(patient: models.Patient) -> models.Patient:

    print("PATIENT OUT: ", patient)
    '''Mapping MIABIS compliant fields to BBMRI.de/GBA Implementation Guide'''

    patient.SEX = apply_map_IG(
        "SEX",
        patient.SEX,
        {
            "Male": "male",
            "Female": "female",
            "Undifferentiated": "undifferentiated",
            "Unknown": "unknown",
        },
    )  

    patient.MATERIAL_TYPE = apply_map_IG(
            "MATERIAL_TYPE",
            patient.MATERIAL_TYPE,
            {"Tissue":"tissue",
            "Tissue (FFPE)" : "tissue-formalin",
            "Tissue (Frozen)":"tissue-frozen",
            "":"tissue-paxgene-or-else",
            "":"tissue-other",
            "Liquid":"liquid",
            "Blood":"whole-blood",
            "Plasma":"blood-plasma",
            "Serum":"blood-serum",
            "":"peripheral-blood-cells-vital",
            "":"buffy-coat",
            "":"bone-marrow",
            "":"csf-liquor",
            "":"ascites",
            "Urine":"urine",
            "Saliva":"saliva",
            "Faeces":"stool-faeces",
            "Other":"liquid-other",
            "":"derivative",
            "DNA":"dna",
            "":"cf-dna",
            "RNA":"rna",
            "Immortalized Cell Lines":"derivative-other",
            },
        ) 

    
    patient.STORAGE_TEMPERATURE = apply_map_IG(
        "STORAGE_TEMPERATURE",
        patient.STORAGE_TEMPERATURE,
        {
            "-60 C to -85 C": "temperature-60to-85",
            "-18 C to -35 C": "temperature-18to-35",
            "2 C to 10 C": "temperature2to10",
            "Other": "temperatureOther",
            "RT":"temperatureRoom",
            "LN":"temperatureLN",
            "GN":"temperatureGN"

        },
    )  
    
    return patient

   

# def convert_temperature(value: str):
#         try:
#             value = int(value)
#             if value < -60 and value > -85:
#                 return "-60 °C to -85 °C"
#             elif value < -18 and value > -35:
#                 return "-18 °C to -35 °C"
#             elif value > 2 and value < 10:
#                 return "2 °C to 10°C"
#             else:
#                 return "Other"
#         except:
#             if value == "RT":
#                 return "RT"
#             elif value == "Liquid nitrogen":
#                 return "LN"
#             elif value == "Gaseous nitrogen":
#                 return "GN"
#             else:
#                 return "Other"

# def normalize_input(patient_data: Dict[str, str]) -> Dict[str, str]:

#     '''Biobank-Specific normalization of input data into MIABIS'''

#     print("PATIENT_DATA BEFORE NORM\n", patient_data)
#     def to_lower(key: str) -> None:
#         if key in patient_data:
#             patient_data[key] = patient_data[key].lower()

#     def to_upper(key: str) -> None:
#         if key in patient_data:
#             patient_data[key] = patient_data[key].upper()

#     def to_title(key: str) -> None:
#         if key in patient_data:
#             patient_data[key] = patient_data[key].title()

#     def convert_unknown_to_zero(key: str) -> None:
#         if key in patient_data:
#             if patient_data[key] == "unknown":
#                 patient_data[key] = 0  # type: ignore
#             if patient_data[key] == "Unknown":
#                 patient_data[key] = 0  # type: ignore

#     def missing_to_unknown(key: str) -> None:
#         if key in patient_data:
#             if patient_data[key] is None:
#                 patient_data[key] = "Unknown"

#     ## Remove extra blank space from value names
#     for key in patient_data:
#         if type(patient_data[key]) == str:
#             patient_data[key] = patient_data[key].strip()


    
            
#     # extract only numbers from PATIENT_ID
#     patient_data["PATIENT_ID"] = re.findall(r"\d+", str(patient_data["PATIENT_ID"]))[0]

#     # convert str into date    
#     # DATE OF BIRTH
#     # if type(patient_data["DATE_DIAGNOSIS"]) == str : patient_data["DATE_DIAGNOSIS"] = datetime.strptime(patient_data["DATE_DIAGNOSIS"], r"%Y-%m-%d")
#     if type(patient_data["DOB"]) == str : patient_data["DOB"] = datetime.strptime(patient_data["DOB"], r"%Y-%m-%d")

#     try:
#         patient_data['DATE_DIAGNOSIS']
#     except: # if there's no diagnosis date, it is equal to year of DOB + AGE_AT_PRIMARY_DIAGNOSIS
#         diagnosis_year = patient_data["DOB"].year + patient_data["AGE_AT_PRIMARY_DIAGNOSIS"]
#         patient_data['DATE_DIAGNOSIS'] = datetime.strptime(f"{diagnosis_year}-01-01", r"%Y-%m-%d")

#     # SAMPLE_MATERIAL_TYPE
#     patient_data['SAMPLE_MATERIAL_TYPE'] = patient_data.pop('SAMPLE_PRESERVATION_MODE')
#     patient_data['SAMPLE_MATERIAL_TYPE'] = apply_map( #aggiungere mapping IFO
#     "SAMPLE_MATERIAL_TYPE",
#     patient_data['SAMPLE_MATERIAL_TYPE'],
#     {   'FFPE': 'Tissue (FFPE)',
#         'SNAP FROZEN': 'Tissue (Frozen)',
#         'BLOOD': 'Blood',
#         'CELL': 'Immortalized Cell Lines',
#         'SNAP': 'Tissue (Frozen)',
#         'FROZEN': 'Tissue (Frozen)',
#         'FRESH FROZEN': 'Tissue (Frozen)',
#         'OCT': 'Tissue (Frozen)',
#         "SN":"Other"} ,#surnatante?
#  ) 

#     # DIAGNOSIS
#     patient_data['DIAGNOSIS'] = patient_data['ICD-10']


#     # # AGE = Date of birth - Sample Collection Date
#     # if type(patient_data['YEAR_OF_SAMPLE_COLLECTION']) == str: 
#     #     age_from_DOB = datetime.strptime(patient_data['YEAR_OF_SAMPLE_COLLECTION'], r"%Y-%m-%d") - patient_data["DOB"]
#     #     patient_data['YEAR_OF_SAMPLE_COLLECTION'] = datetime.strptime(patient_data['YEAR_OF_SAMPLE_COLLECTION'], r"%Y-%m-%d").year
#     # else:
#     #     age_from_DOB = patient_data['YEAR_OF_SAMPLE_COLLECTION'] - patient_data["DOB"]
#     #     patient_data['YEAR_OF_SAMPLE_COLLECTION'] = patient_data['sYEAR_OF_SAMPLE_COLLECTION'].year

#     # if
#     #  not "AGE" in patient_data: patient_data['AGE'] = int(age_from_DOB.days/365) 
#     # patient_data['DONOR_AGE'] = patient_data["DOB"]

#     # DIAGNOSIS
#     # if "." not in patient_data['DIAGNOSIS']: patient_data['DIAGNOSIS'] = patient_data['DIAGNOSIS'][:3] + "." + patient_data['DIAGNOSIS'][3:]

#     # SEX
#     patient_data['SEX'] = apply_map(
#         "SEX",
#         patient_data['SEX'],
#         {
#             "M": "Male",
#             "F": "Female",
#             "undifferentiated": "Undifferentiated",
#             "unknown": "Unknown",
#         },
#     )  

#     # STORAGE TEMPERATURE
#     patient_data['STORAGE_TEMPERATURE'] = convert_temperature(patient_data['STORAGE_TEMPERATURE'])


#     # map colnames:
#     patient_data["AGE_AT_PRIMARY_DIAGNOSIS"] = patient_data.pop("AGE_AT_PRIMARY_DIAGNOSIS")
#     patient_data["GENDER"] = patient_data.pop("SEX")
#     patient_data["TEMP_TYPE"] = patient_data.pop("STORAGE_TEMPERATURE")
#     patient_data["MATERIAL_TYPE"] = patient_data.pop("SAMPLE_MATERIAL_TYPE")
#     patient_data["BIRTH_DATE"] = patient_data.pop("DOB")

#     print("PATIENT_DATA AFTER NORM\n", patient_data)
#     return patient_datas