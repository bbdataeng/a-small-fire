from datetime import date
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel
from pydantic import parse_obj_as
from typing import List

class UNKNOWN(str, Enum):
    UNKNOWN = "Unknown"


class SEX_ENUM(str, Enum):
    FEMALE = "F"
    MALE = "M"
    OTHER = "other"


# # https://training.seer.cancer.gov/colorectal/abstract-code-stage/codes.html
# class HIST_LOCALIZATION_ENUM(str, Enum):
#     # In Appendix 2:
#     # C_180_CAECUM = "C 18.0 - Caecum"
#     # Corrected
#     C_180_CECUM = "C 18.0 - Cecum"
#     C_181_APPENDIX = "C 18.1 - Appendix"
#     C_182_ASCENDING_COLON = "C 18.2 - Ascending colon"
#     C_183_HEPATIC_FLEXURE = "C 18.3 - Hepatic flexure"
#     C_184_TRANSVERSE_COLON = "C 18.4 - Transverse colon"
#     C_185_SPLENIC_FLEXURE = "C 18.5 - Splenic flexure"
#     C_186_DESCENDING_COLON = "C 18.6 - Descending colon"
#     C_187_SIGMOID_COLON = "C 18.7 - Sigmoid colon"
#     # In Appendix 2, replaced:
#     # C_19_RECTOSIGMOID_JUNCTION = "C 19 - Rectosigmoid junction"
#     C_199_RECTOSIGMOID = "C 19.9 - Rectosigmoid junction"
#     C_20_RECTUM = "C 20 - Rectum"


# class HIST_MORPHOLOGY_ENUM(str, Enum):
#     ADENOCARCINOMA = "Adenocarcinoma"
#     ADEONSQUAMOUS_CARCINOMA = "Adeonsquamous carcinoma"
#     HIGHGRADE_NEUROENDOCRINE_CARCINOMA = "High-grade neuroendocrine carcinoma"
#     LARGE_CELL_NEUROENDOCRINE_CARCINOMA = "Large cell neuroendocrine carcinoma"
#     MEDULLARY_CARCINOMA = "Medullary carcinoma"
#     MICROPAPILLARY_CARCINOMA = "Micropapillary carcinoma"
#     MIXED_ADENONEUROENDOCRINE_CARCINOMA = "Mixed adenoneuroendocrine carcinoma"
#     MUCINOUS_CARCINOMA = "Mucinous carcinoma"
#     SERRATED_ADENOCARCINOMA = "Serrated adenocarcinoma"
#     SIGNETRING_CELL_CARCINOMA = "Signet-ring cell carcinoma"
#     SMALL_CELL_NEUROENDOCRINE_CARCINOMA = "small cell neuroendocrine carcinoma"
#     SPINDLE_CELL_CARCINOMA = "Spindle cell carcinoma"
#     SQUAMOUS_CELL_CARCINOMA = "Squamous cell carcinoma"
#     UNDIFFERENTIATED_CARCINOMA = "Undifferentiated carcinoma"
#     OTHER = "Other"



class SAMPLE_MATERIAL_TYPE_ENUM(str, Enum):
    # HEALTHY_COLON_TISSUE = "Healthy colon tissue"
    # TUMOR_TISSUE = "Tumor tissue"
    # OTHER = "Other"
    Tessuto = "Tessuto"
    FFPE = "FFPE"

class SAMPLE_PRESERVATION_MODE_ENUM(str, Enum):
    CRYOPRESERVATION = "Cryopreservation"
    FFPE = "FFPE"
    OTHER = "Other"

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

class SAMPLE_PRESERVATION_MODE_LIST(BaseModel):
    pres: List[SAMPLE_PRESERVATION_MODE_ENUM]


# https://training.seer.cancer.gov/colorectal/abstract-code-stage/codes.html
class DIAGNOSIS_ENUM(str, Enum):
    C_180_CECUM = "C 18.0 - Cecum"
    C_181_APPENDIX = "C 18.1 - Appendix"
    C_182_ASCENDING_RIGHT = "C 18.2 - Ascending (right)"
    C_183_HEPATIC_FLEXURE = "C 18.3 - Hepatic flexure"
    C_184_TRANSVERSE_COLON = "C 18.4 - Transverse colon"
    C_185_SPLENIC_FLEXURE = "C 18.5 - Splenic flexure"
    C_186_DESCENDING_LEFT = "C 18.6 - Descending (left)"
    # In Appendix 2, replaced:
    C_187_SIGMOID = "C 18.7 - Sigmoid"   ## CAMBIATO
    # C_187_SIGMOID = "C 18.7 - Sigmoid colon"
    # In Appendix 2, REMOVED:
    # C_19_RECTOSIGMOID = "C 19 - Rectosigmoid"
    # In Appendix 2 replaced:
    # C_199_RECTOSIGMOID = "C 19.9 - Rectosigmoid"
    C_199_RECTOSIGMOID = "C 19.9 - Rectosigmoid junction"
    C_20_RECTUM = "C 20 - Rectum"
    # C_209_RECTUM = "C 20.9 - Rectum"

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