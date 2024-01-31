from datetime import date, timedelta, datetime
from typing import Dict, Optional, Union

import input_models as models
from loguru import logger as log

from fhir.resources.fhirtypes import Date
import re
import icd10

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
        diag : models.DIAGNOSIS_ENUM
    ) -> str:
        
        # DIAG = models.DIAGNOSIS_ENUM
        # can use icd10 library
        if icd10.exists(diag):
            return diag
        else:
            log.error("Can't map IC10 value for {}", diag)
            return "N/A"
        
        # if diag == DIAG.C_180_CECUM:
        #     return "C18.0 - Cecum"
        # if diag == DIAG.C_181_APPENDIX:
        #     return "C18.1 - Appendix"
        # if diag == DIAG.C_182_ASCENDING_RIGHT:
        #     return "C18.2 - Ascending colon"
        # if diag == DIAG.C_183_HEPATIC_FLEXURE:
        #     return "C18.3 - Hepatic flexure"
        # if diag == DIAG.C_184_TRANSVERSE_COLON:
        #     return "C18.4 - Transverse colon"
        # if diag == DIAG.C_185_SPLENIC_FLEXURE:
        #     return "C18.5 - Splenic flexure"
        # if diag == DIAG.C_186_DESCENDING_LEFT:
        #     return "C18.6 - Descending colon"
        # if diag == DIAG.C_187_SIGMOID:
        #     return "C18.7 - Sigmoid colon"
        # if diag == DIAG.C_199_RECTOSIGMOID:
        #     return "C19.9 - Rectosigmoid junction"
        # if diag == DIAG.C_20_RECTUM:
        #     return "C20 - Rectum"
        # # esempio da continuare

        # log.error("Can't map IC10 value for {}", diag)
        # return "N/A"

 
    

    # # https://samply.github.io/bbmri-fhir-ig/ValueSet-SampleMaterialType.html
    # @staticmethod
    # def get_material_type( 
    #     material_type: models.SAMPLE_MATERIAL_TYPE_ENUM,
    #     material_preservation: models.SAMPLE_PRESERVATION_MODE_ENUM,
    # ) -> Optional[str]:

    #     FROZEN = (
    #         material_preservation
    #         == models.SAMPLE_PRESERVATION_MODE_ENUM.CRYOPRESERVATION
    #     )
    #     FFPE = material_preservation == models.SAMPLE_PRESERVATION_MODE_ENUM.FFPE
    #     HEALTHY = material_type == models.SAMPLE_MATERIAL_TYPE_ENUM.HEALTHY_COLON_TISSUE
    #     TUMOR_TISSUE = material_type == models.SAMPLE_MATERIAL_TYPE_ENUM.TUMOR_TISSUE
    #     OTHER = material_type == models.SAMPLE_MATERIAL_TYPE_ENUM.OTHER

    #     if material_preservation == models.SAMPLE_PRESERVATION_MODE_ENUM.OTHER:
    #         return "tissue-other"
    #     if FROZEN and HEALTHY:
    #         return "normal-tissue-frozen"
    #     if FROZEN and TUMOR_TISSUE:
    #         return "tumor-tissue-frozen"
    #     if FROZEN and OTHER:
    #         return "other-tissue-frozen"
    #     if FFPE and HEALTHY:
    #         return "normal-tissue-ffpe"
    #     if FFPE and TUMOR_TISSUE:
    #         return "tumor-tissue-ffpe"
    #     if FFPE and OTHER:
    #         return "other-tissue-ffpe"
    #     return None


def normalize_input(patient_data: Dict[str, str]) -> Dict[str, str]:
    
    def to_lower(key: str) -> None:
        if key in patient_data:
            patient_data[key] = patient_data[key].lower()

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



# THERAPY_RESPONSE_TIMESTAMP_RELATIVEWEEK
    ## Fix keys
    for dirty_key in list(patient_data):
        key = dirty_key.replace(" ", "_").replace("  ", "")
        patient_data[key] = patient_data[dirty_key]
        if key != dirty_key : del patient_data[dirty_key]
    print("PATIENT_DATA AFTER NORM\n", patient_data)
    ## Fix AGE_AT_PRIMARY_DIAGNOSIS
    
    if type(patient_data["DATE_DIAGNOSIS"]) == str : patient_data["DATE_DIAGNOSIS"] = datetime.strptime(patient_data["DATE_DIAGNOSIS"], r"%Y-%m-%d")
    if type(patient_data["DOB"]) == str : patient_data["DOB"] = datetime.strptime(patient_data["DOB"], r"%Y-%m-%d")

    # AGE_AT_PRIMARY_DIAGNOSIS = Date of birth - Diagnosis Date
    age_diff = patient_data["DATE_DIAGNOSIS"] - patient_data["DOB"]
    patient_data["AGE_AT_PRIMARY_DIAGNOSIS"] = int(age_diff.days/365) 

    # AGE = Date of birth - Sample Collection Date
    age_from_DOB = datetime.strptime(patient_data['YEAR_OF_SAMPLE_COLLECTION'], r"%Y-%m-%d") - patient_data["DOB"]
    patient_data['AGE'] = int(age_from_DOB.days/365) 
    patient_data['DONOR_AGE'] = patient_data["DOB"]

    patient_data['YEAR_OF_SAMPLE_COLLECTION'] = datetime.strptime(patient_data['YEAR_OF_SAMPLE_COLLECTION'], r"%Y-%m-%d").year

    if not "ROOM_TEMPERATURE" in patient_data: patient_data["ROOM_TEMPERATURE"] = "unknown"


    ## AGGIUNTA DI VALORI MANCANTI - PER PROVA
    patient_data['DIAGNOSIS'] = "C18.0"
    # patient_data['SAMPLE_MATERIAL_TYPE'] = "Tumor tissue"
    # patient_data['SAMPLE_PRESERVATION_MODE'] = "FFPE"
    print("PATIENT_DATA AFTER NORM\n", patient_data)
    return patient_data


def apply_map(label: str, value: str, mapping: Dict[str, str]) -> str:

    if value not in mapping:
        raise ValueError(f"Invalid value for {label}: {value}")

    return mapping[value]



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
             "FFPE":"tissue",
            "" : "tissue-formalin",
            "":"tissue-frozen",
            "":"tissue-paxgene-or-else",
            "":"tissue-other",
            "":"liquid",
            "":"whole-blood",
            "":"blood-plasma",
            "":"blood-serum",
            "":"peripheral-blood-cells-vital",
            "":"buffy-coat",
            "":"bone-marrow",
            "":"csf-liquor",
            "":"ascites",
            "":"urine",
            "":"saliva",
            "":"stool-faeces",
            "":"liquid-other",
            "":"derivative",
            "":"dna",
            "":"cf-dna",
            "":"rna",
            "":"derivative-other",
            },
        ) 

    patient.ROOM_TEMPERATURE = apply_map(
        "ROOM_TEMPERATURE",
        patient.ROOM_TEMPERATURE,
        {
            "":"temperature2to10",
            "":"temperature-18to-35",
            "":"temperature-60to-85",
            "":"temperatureGN",
            "":"temperatureLN",
            "":"temperatureRoom",
            "unknown":"temperatureOther"
        },
    )  # type: ignore



    return patient
