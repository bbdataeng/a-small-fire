from datetime import date, timedelta, datetime
from typing import Dict, Optional, Union, Any

import input_models as models
from loguru import logger as log

from fhir.resources.fhirtypes import Date
import re
import yaml
from input_models import MATERIAL_TYPE_ENUM, STORAGE_TEMPERATURE_ENUM, SEX_ENUM

# import icd10


class FHIRNormalization:

    # https://www.icd10data.com/search
    @staticmethod
    def get_diagnosis_icd10(diag: str) -> str:
        return diag


def apply_map(label: str, value: str, mapping: Dict[str, str]) -> str:
    for miabis_value, biobank_values in mapping.items():
        # print('value:', value)
        if isinstance(biobank_values, str):
            # if a single string, convert it to a list
            biobank_values = [biobank_values]
        # print('biobank_values:', biobank_values)
        if value in biobank_values:
            # print('miabis_value:', miabis_value)
            return miabis_value
    return value  # leave the wrong value to better debugging


def apply_map_IG(label: str, value: str, mapping: Dict[str, str]) -> str:

    if value not in mapping:
        raise ValueError(f"Invalid value for {label}: {value}")

    return mapping[value]


def load_config(config_path: str) -> Dict:
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


## -------------------- Input Normalization [Optional] --------------------- ##
## ------ Mapping to MIABIS standard according to mapping_config.yml ------- ##


def normalize_input(patient_data: Dict[str, Any], config_path: str) -> Dict[str, Any]:
    """Normalize input data based on configuration"""

    config = load_config(config_path)
    field_mappings = config.get("field_mappings", {})
    value_mappings = config.get("value_mappings", {})

    # field name mappings
    for miabis_field, biobank_field in field_mappings.items():
        if biobank_field in patient_data:
            patient_data[miabis_field] = patient_data.pop(biobank_field)

    patient_data["STORAGE_TEMPERATURE"] = str(patient_data["STORAGE_TEMPERATURE"])
    # value mappings
    for key, mapping in value_mappings.items():
        # print("KEY: ", key)
        # print("MAPPING: ", mapping)
        # print("patient_data[key]", patient_data[key])
        if key in patient_data:
            patient_data[key] = apply_map(key, patient_data[key], mapping)

    # try:
    #     patient_data['DATE_DIAGNOSIS']
    # except: # if there's no diagnosis date, it is equal to year of DOB + AGE_AT_PRIMARY_DIAGNOSIS
    #     diagnosis_year = patient_data["BIRTH_DATE"].year + patient_data["AGE_AT_PRIMARY_DIAGNOSIS"]
    #     patient_data['DATE_DIAGNOSIS'] = datetime.strptime(f"{diagnosis_year}-01-01", r"%Y-%m-%d")

    # print("patient_data: ", patient_data)

    return patient_data


## ------------------------- Output Normalization -------------------------- ##
## ----------------- Mapping to FHIR values (BBMRI.de IG) ------------------ ##


def normalize_output(patient: models.Patient) -> models.Patient:
    """Mapping MIABIS compliant fields to BBMRI.de/GBA Implementation Guide"""

    patient.SEX = apply_map_IG(
        "SEX",
        patient.SEX,
        {
            SEX_ENUM.M.value: "male",
            SEX_ENUM.F.value: "female",
            SEX_ENUM.UNDIFFERENTIATED.value: "undifferentiated",
            SEX_ENUM.UNKNOWN.value: "unknown",
        },
    )

    patient.MATERIAL_TYPE = apply_map_IG(
        "MATERIAL_TYPE",
        patient.MATERIAL_TYPE,
        {
            MATERIAL_TYPE_ENUM.ANY.value: "unknown",
            MATERIAL_TYPE_ENUM.BUFFY_COAT.value: "buffy-coat",
            MATERIAL_TYPE_ENUM.CDNA_MRNA.value: "rna",
            MATERIAL_TYPE_ENUM.CELL_LINES.value: "derivative-other",
            MATERIAL_TYPE_ENUM.DNA.value: "dna",
            MATERIAL_TYPE_ENUM.FECES.value: "stool-faeces",
            MATERIAL_TYPE_ENUM.MICRORNA.value: "rna",
            MATERIAL_TYPE_ENUM.NASAL_SWAB.value: "swab",
            MATERIAL_TYPE_ENUM.NOT_AVAILABLE.value: "unknown",
            MATERIAL_TYPE_ENUM.OTHER.value: "liquid-other",
            MATERIAL_TYPE_ENUM.PATHOGEN.value: "unknown-pathogen",
            MATERIAL_TYPE_ENUM.PERIPHERAL_BLOOD_CELLS.value: "peripheral-blood-cells-vital",
            MATERIAL_TYPE_ENUM.PLASMA.value: "blood-plasma",
            MATERIAL_TYPE_ENUM.RNA.value: "rna",
            MATERIAL_TYPE_ENUM.SALIVA.value: "saliva",
            MATERIAL_TYPE_ENUM.SERUM.value: "blood-serum",
            MATERIAL_TYPE_ENUM.THROAT_SWAB.value: "swab",
            MATERIAL_TYPE_ENUM.TISSUE_FROZEN.value: "tissue-frozen",
            MATERIAL_TYPE_ENUM.TISSUE_PARAFIN_PRESERVED.value: "tissue-ffpe",
            MATERIAL_TYPE_ENUM.TISSUE_STAINED_SECTIONS.value: "tissue-other",
            MATERIAL_TYPE_ENUM.URINE.value: "urine",
            MATERIAL_TYPE_ENUM.WHOLE_BLOOD.value: "whole-blood",
        },
    )

    patient.STORAGE_TEMPERATURE = apply_map_IG(
        "STORAGE_TEMPERATURE",
        patient.STORAGE_TEMPERATURE,
        {
            STORAGE_TEMPERATURE_ENUM.MIN60TOMIN85.value: "temperature-60to-85",
            STORAGE_TEMPERATURE_ENUM.MIN18TOMIN36.value: "temperature-18to-35",
            STORAGE_TEMPERATURE_ENUM.TEMMP2TO10.value: "temperature2to10",
            STORAGE_TEMPERATURE_ENUM.OTHER.value: "temperatureOther",
            STORAGE_TEMPERATURE_ENUM.RT.value: "temperatureRoom",
            STORAGE_TEMPERATURE_ENUM.LN.value: "temperatureLN",
            # "GN":"temperatureGN"
        },
    )

    return patient
