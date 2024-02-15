from datetime import date
from enum import Enum, auto
from typing import Optional, Union
from pydantic import BaseModel, root_validator
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
    DIAGNOSIS : str

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

    @root_validator
    def validate_fields(cls, values):
        diagnosis_value = values.get('DIAGNOSIS')

        if diagnosis_value and diagnosis_value not in codici_icd:
            raise ValueError(f"DIAGNOSIS must be one of the values in the list {codici_icd}")
        return values




codici_icd = [i[:3] + "." + i[3:]  for i in icd10.codes.keys() if i.startswith("C")]







