from datetime import date
from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel
from pydantic import parse_obj_as
from typing import List

# all the possible values for the input employed in the validation and normalization process.

class UNKNOWN(str, Enum):
    UNKNOWN = "Unknown"

class SEX_ENUM(str, Enum):
    FEMALE = "F"
    MALE = "M"
    OTHER = "other"

class SAMPLE_MATERIAL_TYPE_ENUM(str, Enum):
    # HEALTHY_COLON_TISSUE = "Healthy colon tissue"
    # TUMOR_TISSUE = "Tumor tissue"
    # OTHER = "Other"
    Tessuto = "Tessuto"
    FFPE = "FFPE"

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


# https://training.seer.cancer.gov/colorectal/abstract-code-stage/codes.html
class DIAGNOSIS_ENUM(str, Enum):
    C18 = "C18.0"

class ROOM_TEMPERATURE_ENUM(str, Enum):
    pass
	# "temperature2to10",
	# "temperature-18to-35",
	# "temperature-60to-85",
	# "temperatureGN",
	# "temperatureLN",
	# "temperatureRoom",
	# "temperatureOther",

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
    ROOM_TEMPERATURE: Optional[str]