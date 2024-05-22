from datetime import date
from enum import Enum, auto
from typing import Optional, Union
from pydantic import BaseModel, root_validator
from pydantic import parse_obj_as
from typing import List
import simple_icd_10 as icd

# import icd10

# all the possible values for the input employed in the validation and normalization process.

class UNKNOWN(str, Enum):
    UNKNOWN = "Unknown"

class SEX_ENUM(str, Enum):
    F = "Female"
    M = "Male"
    unknown = "Unknown"
    undifferentiated = "Undifferentiated"

class SAMPLE_MATERIAL_TYPE_ENUM(str, Enum):
    TISSUE_FFPE = 'Tissue (FFPE)'
    TISSUE_FROZEN = 'Tissue (Frozen)'
    BLOOD = 'Blood'
    CELL = 'Immortalized Cell Lines'
    DNA = 'DNA'
    RNA = 'RNA'
    FAECES = 'Faeces'
    PATHOGEN = 'Isolated Pathogen'
    PLASMA = 'Plasma'
    OTHER = 'Other'
    SALIVA = 'Saliva'
    SERUM = 'Serum'
    URINE = 'Urine'



class STORAGE_TEMPERATURE_ENUM(str, Enum):
    MIN60TOMIN85 = "-60 °C to -85 °C"
    MIN18TOMIN36 = "-18 °C to -35 °C"
    TEMMP2TO10 = "2 °C to 10°C"
    OTHER ="Other"
    RT = "RT"
    GN = "GN"
    LN = "LN"


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
    # Dignosis (ICD-10)
    DIAGNOSIS : str
    # Donor Age
    DONOR_AGE : date
    # AGE: int

    # ########## Sample
    # Sample ID
    SAMPLE_ID: Optional[str]
    # Material type
    SAMPLE_MATERIAL_TYPE: SAMPLE_MATERIAL_TYPE_ENUM
    # Year of sample collection
    # YEAR_OF_SAMPLE_COLLECTION: int
    SAMPLING_DATE: date
    # Room temperature
    STORAGE_TEMPERATURE: STORAGE_TEMPERATURE_ENUM

    @root_validator
    def validate_fields(cls, values):
        diagnosis_value = values.get('DIAGNOSIS')

        # with open(r'codici_icd.txt', 'r') as fp:
        #     codici_icd = fp.read().split('\n')[:-1]
        #     diagnosis_value = values.get('DIAGNOSIS')
            # codici_icd = [i[:3] + "." + i[3:]  for i in icd10.codes.keys() if i.startswith("C")] # neoplasms only
        # codici_icd = [i[:3] + "." + i[3:]  for i in icd10.codes.keys()] # all ICDs
        # codici_icd = [i  for i in icd10.codes.keys()] # all ICDs

        icd_val = diagnosis_value.replace(".", "")
        if icd_val and not icd.is_valid_item(icd_val):
            raise ValueError(f"DIAGNOSIS must be a valid ICD-10 code")
        return values












