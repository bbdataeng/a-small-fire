from datetime import date
from enum import Enum, auto
from typing import Optional, Union
from pydantic import BaseModel, root_validator, validator
from pydantic import parse_obj_as
from typing import List
import simple_icd_10 as icd

# import icd10

# all the possible values for the input employed in the validation and normalization process.
# should be MIABIS model

class UNKNOWN(str, Enum):
    UNKNOWN = "Unknown"

class SEX_ENUM(str, Enum):
    F = "Female"
    M = "Male"
    unknown = "Unknown"
    undifferentiated = "Undifferentiated"

class SAMPLE_MATERIAL_TYPE_ENUM(str, Enum):
    TISSUE_FFPE = 'TissueFFPE'
    TISSUE_FROZEN = 'TissueFrozen'
    BLOOD = 'Blood'
    CELL = 'ImmortalizedCellLines'
    DNA = 'DNA'
    RNA = 'RNA'
    FAECES = 'Faeces'
    PATHOGEN = 'IsolatedPathogen'
    PLASMA = 'Plasma'
    OTHER = 'Other'
    SALIVA = 'Saliva'
    LIQUOR = 'Liquor'
    SERUM = 'Serum'
    URINE = 'Urine'


class STORAGE_TEMPERATURE_ENUM(str, Enum):
    # MIN60TOMIN85 = "temperature-60to-85"
    # MIN18TOMIN36 = "temperature-18to-36"
    # TEMMP2TO10 = "temperature1to10"
    # OTHER ="temperatureOther"
    # RT = "temperatureRoom"
    # LN = "temperatureLN"

    MIN60TOMIN85 = "-60to-85"
    MIN18TOMIN36 = "-18to-35"
    TEMMP2TO10 = "2to10"
    OTHER ="Other"
    RT = "RT"
    LN = "LN"

class Patient(BaseModel):

    # ########## Patient Data ##########
    # Patient pseudonym
    PATIENT_ID: Optional[str]
    # Age at diagnosis (rounded to years)
    DIAGNOSIS_AGE: int
    # Biological sex
    SEX: SEX_ENUM
    # Date of diagnosis
    DATE_DIAGNOSIS: date
    # Dignosis (ICD-10)
    DIAGNOSIS : str
    DIAGNOSIS2: Optional[str]
    # Donor Age
    BIRTH_DATE : Optional[date]
    DONOR_AGE: Optional[int]

    # ############# Sample #############
    # Sample ID
    SAMPLE_ID: Optional[str]
    # Material type
    MATERIAL_TYPE: SAMPLE_MATERIAL_TYPE_ENUM
    # Year of sample collection
    # YEAR_OF_SAMPLE_COLLECTION: int
    SAMPLING_DATE: date
    # Room temperature
    STORAGE_TEMPERATURE: STORAGE_TEMPERATURE_ENUM


    
    @validator('DIAGNOSIS')
    def check_icd(cls, v):
        if v:
            icd_val = v.replace(".", "")
            if not icd.is_valid_item(icd_val):
                raise ValueError(f"DIAGNOSIS must be a valid ICD-10 code")
        return v










