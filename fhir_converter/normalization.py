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
    @staticmethod
    # def get_collection_date(collection_year: int, surgery: Date) -> Date:
    #     return surgery or Date(collection_year, 1, 1)
    def get_collection_date(collection_year: int) -> Date:
        return Date(collection_year, 1, 1)
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


    ## Fix keys
    for dirty_key in list(patient_data):
        key = dirty_key.replace(" ", "_").replace("  ", "").upper()
        patient_data[key] = patient_data[dirty_key]
        if key != dirty_key : del patient_data[dirty_key]

    # convert str into date    
    if type(patient_data["DATE_DIAGNOSIS"]) == str : patient_data["DATE_DIAGNOSIS"] = datetime.strptime(patient_data["DATE_DIAGNOSIS"], r"%Y-%m-%d")
    if type(patient_data["DOB"]) == str : patient_data["DOB"] = datetime.strptime(patient_data["DOB"], r"%Y-%m-%d")

    # AGE_AT_PRIMARY_DIAGNOSIS = Date of birth - Diagnosis Date
    age_diff = patient_data["DATE_DIAGNOSIS"] - patient_data["DOB"]
    patient_data["AGE_AT_PRIMARY_DIAGNOSIS"] = int(age_diff.days/365) 

    # AGE = Date of birth - Sample Collection Date
    if type(patient_data['YEAR_OF_SAMPLE_COLLECTION']) == str: 
        age_from_DOB = datetime.strptime(patient_data['YEAR_OF_SAMPLE_COLLECTION'], r"%Y-%m-%d") - patient_data["DOB"]
        patient_data['YEAR_OF_SAMPLE_COLLECTION'] = datetime.strptime(patient_data['YEAR_OF_SAMPLE_COLLECTION'], r"%Y-%m-%d").year
    else:
        age_from_DOB = patient_data['YEAR_OF_SAMPLE_COLLECTION'] - patient_data["DOB"]
        patient_data['YEAR_OF_SAMPLE_COLLECTION'] = patient_data['YEAR_OF_SAMPLE_COLLECTION'].year

    if not "AGE" in patient_data: patient_data['AGE'] = int(age_from_DOB.days/365) 
    patient_data['DONOR_AGE'] = patient_data["DOB"]

    

    ## AGGIUNTA valori mancanti - PER PROVA 
    # patient_data['DIAGNOSIS'] = "C18.0"
    # if not "STORAGE_TEMPERATURE" in patient_data: patient_data["STORAGE_TEMPERATURE"] = -80
    # patient_data["STORAGE_TEMPERATURE"] = str(patient_data['STORAGE_TEMPERATURE'])

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
                return "temperature-60to-85"
            elif value < -18 and value > -35:
                return "temperature-18to-35"
            elif value > 2 and value < 10:
                return "temperature2to10"
            else:
                return "temperatureOther"
        except:
            if value == "RT":
                return "temperatureRoom"
            elif value == "Liquid nitrogen":
                return "temperatureLN"
            elif value == "Gaseous nitrogen":
                return "temperatureGN"
            else:
                return "temperatureOther"
            
def normalize_output(patient: models.Patient) -> models.Patient:
    '''mapping of values according to BBMRI.de/GBA Implementation Guide'''

    patient.SEX = apply_map(
        "SEX",
        patient.SEX,
        {
            "M": "male",
            "F": "female",
            "other": "other",
            "unknown": "unknown",
        },
    )  # type: ignore

    patient.SAMPLE_MATERIAL_TYPE = apply_map(
            "SAMPLE_MATERIAL_TYPE",
            patient.SAMPLE_MATERIAL_TYPE,
            {"Tessuto":"tissue",
            "FFPE" : "tissue-formalin",
            "":"tissue-frozen",
            "":"tissue-paxgene-or-else",
            "":"tissue-other",
            "Liquid":"liquid",
            "Whole blood":"whole-blood",
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
            "":"liquid-other",
            "":"derivative",
            "DNA":"dna",
            "":"cf-dna",
            "RNA":"rna",
            "":"derivative-other",
            },
        ) 

    patient.STORAGE_TEMPERATURE = convert_temperature(patient.STORAGE_TEMPERATURE)
    

    
    return patient


