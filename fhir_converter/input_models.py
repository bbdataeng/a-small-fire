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
    UNKNOWN = "Unknown"
    UNDIFFERENTIATED = "Undifferentiated"

from enum import Enum

class MATERIAL_TYPE_ENUM(str, Enum):
    ANY = 'Any'
    BUFFY_COAT = 'Buffy Coat'
    CDNA_MRNA = 'cDNA / mRNA'
    CELL_LINES = 'Cell lines'
    DNA = 'DNA'
    FECES = 'Feces'
    MICRORNA = 'microRNA'
    NASAL_SWAB = 'Nasal swab'
    NOT_AVAILABLE = 'Not available'
    OTHER = 'Other'
    PATHOGEN = 'Pathogen'
    PERIPHERAL_BLOOD_CELLS = 'Peripheral blood cells'
    PLASMA = 'Plasma'
    RNA = 'RNA'
    SALIVA = 'Saliva'
    SERUM = 'Serum'
    THROAT_SWAB = 'Throat swab'
    TISSUE_FROZEN = 'Tissue (frozen)'
    TISSUE_PARAFIN_PRESERVED = 'Tissue (paraffin preserved)'
    TISSUE_STAINED_SECTIONS = 'Tissue (stained sections/slides)'
    URINE = 'Urine'
    WHOLE_BLOOD = 'Whole Blood'


class STORAGE_TEMPERATURE_ENUM(str, Enum):
    MIN60TOMIN85 = "-60°C to -80°C"
    MIN18TOMIN36 = "-18°C to -35°C"
    TEMMP2TO10 = "2°C to 10°C"
    OTHER ="Other"
    RT = "Room temperature"
    LN = "Liquid Nitrogen"

    # MIN60TOMIN85 = "temperature-60to-85"
    # MIN18TOMIN36 = "temperature-18to-36"
    # TEMMP2TO10 = "temperature1to10"
    # OTHER ="temperatureOther"
    # RT = "temperatureRoom"
    # LN = "temperatureLN"



class Patient(BaseModel):

    # ########## Patient Data ##########
    # Patient pseudonym
    PATIENT_ID: Optional[str]
    # Age at diagnosis (rounded to years)
    DIAGNOSIS_DONOR_AGE: int
    # Biological sex
    SEX: SEX_ENUM
    # Date of diagnosis
    DIAGNOSIS_DATE: date

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
    MATERIAL_TYPE: MATERIAL_TYPE_ENUM
    # Year of sample collection
    # YEAR_OF_SAMPLE_COLLECTION: int
    SAMPLING_DATE: date
    # Room temperature
    STORAGE_TEMPERATURE: STORAGE_TEMPERATURE_ENUM


    # validator for Diagnosis - must be valid icd-10 code
    @validator('DIAGNOSIS')
    def check_icd(cls, v):
        if v:
            icd_val = v.replace(".", "")
            if not icd.is_valid_item(icd_val):
                raise ValueError(f"DIAGNOSIS must be a valid ICD-10 code")
        return v










