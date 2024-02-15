from datetime import date
from enum import Enum, auto
from typing import Optional, Union
from pydantic import BaseModel
from pydantic import parse_obj_as
from typing import List
import icd10

# all the possible values for the input employed in the validation and normalization process.

class UNKNOWN(str, Enum):
    UNKNOWN = "Unknown"

class SEX_ENUM(str, Enum):
    F = "F"
    M = "M"
    other = "other"

class SAMPLE_MATERIAL_TYPE_ENUM(str, Enum):
    Tissue = "Tessuto"
    FFPE = "FFPE"
    Liquid = "Liquido"
    Blood = "Sangue"
    Saliva = "Saliva"
    Urine = "Urine"
    RNA = "RNA"
    DNA = "DNA"

    # "tissue",
	# "tissue-formalin",
	# "tissue-frozen",
	# "tissue-paxgene-or-else",
	# "tissue-other",
	# "liquid",
	# "whole-blood",
	# "blood-plasma",
	# "blood-serum",
	# "peripheral-blood-cells-vital",
	# "buffy-coat",
	# "bone-marrow",
	# "csf-liquor",
	# "ascites",
	# "urine",
	# "saliva",
	# "stool-faeces",
	# "liquid-other",
	# "derivative",
	# "dna",
	# "cf-dna",
	# "rna",
	# "derivative-other",

class DIAGNOSIS_ENUM(str, Enum):
    C18 = "C18.0"
#     DEFAULT = auto()

# codici_icd  = [i for i in icd10.codes.keys() if i.startswith("C")]
# for codice in codici_icd:
#     setattr(DIAGNOSIS_ENUM, f'{codice}', f"{codice[:3]}.{codice[3:]}")



# class STORAGE_TEMPERATURE_ENUM(str, Enum):
#     RT = "RT"
#     TEMP_2to10 = "2C to 10C"
#     TEMP_18to35 = "-18C to -35C"
#     TEMP_60to85 = "-60C to -85C"
#     TEMP_GN = "Liquid nitrogen vapor phase"
#     TEMP_LN = "Liquid nitrogen liquid phase"
#     TEMP_other = "Other"


# def convert_temperature(value: str) -> STORAGE_TEMPERATURE_ENUM:
#     try:
#         int(value)
#         if value < -60 and value > -85:
#             return STORAGE_TEMPERATURE_ENUM.TEMP_60to85
#         elif value < -18 and value > -35:
#             return STORAGE_TEMPERATURE_ENUM.TEMP_18to35
#         else:
#             return STORAGE_TEMPERATURE_ENUM.TEMP_other
#     except:
#         if value == "RT":
#             return STORAGE_TEMPERATURE_ENUM.RT
#         elif value == "Liquid nitrogen":
#             return STORAGE_TEMPERATURE_ENUM.TEMP_LN
#         else:
#             return STORAGE_TEMPERATURE_ENUM.TEMP_other




class Patient(BaseModel):

    # ########## Patient Data
    # Patient pseudonym
    PATIENT_ID: Optional[str]
    # Age at diagnosis (rounded to years)
    AGE_AT_PRIMARY_DIAGNOSIS: int
    # Biological sex
    SEX: SEX_ENUM
    # Date of diagnosis
    DATE_DIAGNOSIS: date
    DIAGNOSIS : DIAGNOSIS_ENUM

    DONOR_AGE : date
    # AGE: int
    # ########## Sample
    # Sample ID
    SAMPLE_ID: str
    # Material type
    SAMPLE_MATERIAL_TYPE: SAMPLE_MATERIAL_TYPE_ENUM
    # Preservation mode
    # SAMPLE_PRESERVATION_MODE: SAMPLE_PRESERVATION_MODE_ENUM
    # SAMPLE_PRESERVATION_MODE: List[SAMPLE_PRESERVATION_MODE_ENUM]
    # Year of sample collection
    YEAR_OF_SAMPLE_COLLECTION: int
    # Room temperature
    STORAGE_TEMPERATURE: Optional[str]