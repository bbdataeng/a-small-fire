from datetime import date, timedelta, datetime
from typing import Dict, Optional, Union

import input_models as models
from loguru import logger as log

from fhir.resources.fhirtypes import Date
import re
# import icd10


class FHIRNormalization:
    @staticmethod
    def get_date_from_rel(diagnosis: date, weeks: float) -> Optional[date]:
        # When 0 is intended to be Unknown
        if weeks <= 0:
            return None
        days: int = round(weeks * 7)
        return diagnosis + timedelta(days=days)

    # Return surgery date, if any
    # otherwise return collection year at 1st of January
    # @staticmethod
    # def get_collection_date(collection_year: int, surgery: Date) -> Date:
    #     return surgery or Date(collection_year, 1, 1)
    # def get_collection_date(collection_year: int) -> Date:
    #     return Date(collection_year, 1, 1)
    # https://www.icd10data.com/search
    @staticmethod
    def get_diagnosis_icd10(
        diag : str
    ) -> str:
        # DIAG = models.DIAGNOSIS_ENUM
        # can use icd10 library
        # if icd10.exists(diag):
        #     return diag
        # else:
        #     log.error("Can't map IC10 value for {}", diag)
        #     return "N/A"
        return diag



def normalize_input(patient_data: Dict[str, str]) -> Dict[str, str]:

    '''Biobank-Specific normalization of input data'''
    print("PATIENT_DATA BEFORE NORM\n", patient_data)
    def to_lower(key: str) -> None:
        if key in patient_data:
            patient_data[key] = patient_data[key].lower()

    def to_upper(key: str) -> None:
        if key in patient_data:
            patient_data[key] = patient_data[key].upper()

    def to_title(key: str) -> None:
        if key in patient_data:
            patient_data[key] = patient_data[key].title()

    def convert_unknown_to_zero(key: str) -> None:
        if key in patient_data:
            if patient_data[key] == "unknown":
                patient_data[key] = 0  # type: ignore
            if patient_data[key] == "Unknown":
                patient_data[key] = 0  # type: ignore

    def missing_to_unknown(key: str) -> None:
        if key in patient_data:
            if patient_data[key] is None:
                patient_data[key] = "Unknown"

    ## Remove extra blank space from value names
    for key in patient_data:
        if type(patient_data[key]) == str:
            patient_data[key] = patient_data[key].strip()

    # ## Fix keys
    # for dirty_key in list(patient_data):
    #     key = dirty_key.replace(" ", "_").replace("  ", "").upper()
    #     patient_data[key] = patient_data[dirty_key]
    #     if key != dirty_key : del patient_data[dirty_key]


    
            
    # extract only numbers from PATIENT_ID
    patient_data["PATIENT_ID"] = re.findall(r"\d+", str(patient_data["PATIENT_ID"]))[0]

    # convert str into date    
    # DATE OF BIRTH
    # if type(patient_data["DATE_DIAGNOSIS"]) == str : patient_data["DATE_DIAGNOSIS"] = datetime.strptime(patient_data["DATE_DIAGNOSIS"], r"%Y-%m-%d")
    if type(patient_data["DOB"]) == str : patient_data["DOB"] = datetime.strptime(patient_data["DOB"], r"%Y-%m-%d")

    try:
        patient_data['DATE_DIAGNOSIS']
    except:
        diagnosis_year = patient_data["DOB"].year - patient_data["AGE_AT_PRIMARY_DIAGNOSIS"]
        patient_data['DATE_DIAGNOSIS'] = datetime.strptime(f"{diagnosis_year}-01-01", r"%Y-%m-%d")

    # SAMPLE_MATERIAL_TYPE
    patient_data['SAMPLE_MATERIAL_TYPE'] = patient_data.pop('SAMPLE_PRESERVATION_MODE')
    patient_data['SAMPLE_MATERIAL_TYPE'] = apply_map( #aggiungere mapping IFO
    "SAMPLE_MATERIAL_TYPE",
    patient_data['SAMPLE_MATERIAL_TYPE'],
    {   'FFPE': 'Tissue (FFPE)',
        'SNAP FROZEN': 'Tissue (Frozen)',
        'BLOOD': 'Blood',
        'CELL': 'Immortalized Cell Lines',
        'SNAP': 'Tissue (Frozen)',
        'FROZEN': 'Tissue (Frozen)',
        'FRESH FROZEN': 'Tissue (Frozen)',
        'OCT': 'Tissue (Frozen)',
        "SN":"Other"} ,#surnatante?
 ) 

    # DIAGNOSIS
    patient_data['DIAGNOSIS'] = patient_data['ICD-10']


    # # AGE = Date of birth - Sample Collection Date
    # if type(patient_data['YEAR_OF_SAMPLE_COLLECTION']) == str: 
    #     age_from_DOB = datetime.strptime(patient_data['YEAR_OF_SAMPLE_COLLECTION'], r"%Y-%m-%d") - patient_data["DOB"]
    #     patient_data['YEAR_OF_SAMPLE_COLLECTION'] = datetime.strptime(patient_data['YEAR_OF_SAMPLE_COLLECTION'], r"%Y-%m-%d").year
    # else:
    #     age_from_DOB = patient_data['YEAR_OF_SAMPLE_COLLECTION'] - patient_data["DOB"]
    #     patient_data['YEAR_OF_SAMPLE_COLLECTION'] = patient_data['sYEAR_OF_SAMPLE_COLLECTION'].year

    # if
    #  not "AGE" in patient_data: patient_data['AGE'] = int(age_from_DOB.days/365) 
    # patient_data['DONOR_AGE'] = patient_data["DOB"]

    # DIAGNOSIS
    if "." not in patient_data['DIAGNOSIS']: patient_data['DIAGNOSIS'] = patient_data['DIAGNOSIS'][:3] + "." + patient_data['DIAGNOSIS'][3:]

    # SEX
    patient_data['SEX'] = apply_map(
        "SEX",
        patient_data['SEX'],
        {
            "M": "Male",
            "F": "Female",
            "undifferentiated": "Undifferentiated",
            "unknown": "Unknown",
        },
    )  

    # STORAGE TEMPERATURE
    patient_data['STORAGE_TEMPERATURE'] = convert_temperature(patient_data['STORAGE_TEMPERATURE'])

    print("PATIENT_DATA AFTER NORM\n", patient_data)
    return patient_data


def apply_map(label: str, value: str, mapping: Dict[str, str]) -> str:

    if value not in mapping:
        raise ValueError(f"Invalid value for {label}: {value}")

    return mapping[value]

def convert_temperature(value: str):
        try:
            value = int(value)
            if value < -60 and value > -85:
                return "-60 °C to -85 °C"
            elif value < -18 and value > -35:
                return "-18 °C to -35 °C"
            elif value > 2 and value < 10:
                return "2 °C to 10°C"
            else:
                return "Other"
        except:
            if value == "RT":
                return "RT"
            elif value == "Liquid nitrogen":
                return "LN"
            elif value == "Gaseous nitrogen":
                return "GN"
            else:
                return "Other"

            
def normalize_output(patient: models.Patient) -> models.Patient:

    '''Mapping MIABIS compliant fields to BBMRI.de/GBA Implementation Guide'''

    patient.SEX = apply_map(
        "SEX",
        patient.SEX,
        {
            "Male": "male",
            "Female": "female",
            "Undifferentiated": "undifferentiated",
            "Unknown": "unknown",
        },
    )  

    patient.SAMPLE_MATERIAL_TYPE = apply_map(
            "SAMPLE_MATERIAL_TYPE",
            patient.SAMPLE_MATERIAL_TYPE,
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

    
    patient.STORAGE_TEMPERATURE = apply_map(
        "STORAGE_TEMPERATURE",
        patient.STORAGE_TEMPERATURE,
        {
            "-60 °C to -85 °C": "temperature-60to-85",
            "-18 °C to -35 °C": "temperature-18to-35",
            "2 °C to 10°C": "temperature2to10",
            "Other": "temperatureOther",
            "RT":"temperatureRoom",
            "LN":"temperatureLN",
            "GN":"temperatureGN"

        },
    )  
    
    return patient


