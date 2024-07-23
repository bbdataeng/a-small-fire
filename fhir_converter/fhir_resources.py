from datetime import date
from typing import List, Optional, Tuple, Union
from uuid import uuid4
import yaml

import input_models as models
from loguru import logger as log
from normalization import FHIRNormalization

from fhir.resources.address import Address
from fhir.resources.bundle import Bundle
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.codeablereference import CodeableReference
from fhir.resources.coding import Coding
from fhir.resources.condition import Condition
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.extension import Extension
from fhir.resources.fhirtypes import AgeType, DosageType, String
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.meta import Meta
from fhir.resources.observation import Observation
from fhir.resources.organization import Organization
from fhir.resources.patient import Patient
from fhir.resources.period import Period
from fhir.resources.procedure import Procedure
from fhir.resources.reference import Reference
from fhir.resources.specimen import Specimen, SpecimenCollection
from fhir.resources.age import Age

"""
fhir_resources.py -------------------------------------------------------------
Employed by the FHIR-MODEL module to map each field/entity to its FHIR counterpart 
"""

# Configuration Info
with open("general_config.yaml", "r") as config_file:
    config_data = yaml.safe_load(config_file)

BBMRI_STRUCTURE_DEFINITION_URL = config_data.get("bbmri_structure_definition_url", "")
SERVER_URL = config_data.get("server_url", "")
ORGANIZATION_ID_COLL = config_data.get("collection_id", "")
ORGANIZATION_NAME_COLL = config_data.get("collection_name", "")
ORGANIZATION_ALIAS_COLL = config_data.get("collection_alias", [])
ORGANIZATION_CONTACT_COLL = config_data.get("collection_contact", [])
ORGANIZATION_ID_BIO = config_data.get("biobank_id", "")
ORGANIZATION_NAME_BIO = config_data.get("biobank_name", "")
ORGANIZATION_ALIAS_BIO = config_data.get("biobank_alias", [])
ORGANIZATION_CONTACT_BIO = config_data.get("biobank_contact", [])


# Search on https://icd.who.int/browse10/2019/en
ICD10_SYSTEM = "http://hl7.org/fhir/sid/icd-10"
SNOMED_SYSTEM = "http://snomed.info/sct"


# Got from import_sample-synthetic_data-FHIR.json
SAMPLE_MATERIAL_TYPE_SYSTEM = "https://fhir.bbmri.de/CodeSystem/SampleMaterialType"
STORAGE_TEMPERATURE_SYSTEM = "https://fhir.bbmri.de/CodeSystem/StorageTemperature"


class FHIRResources:
    @staticmethod
    def get_meta(profile: str) -> Meta:
        return Meta(profile=[f"{BBMRI_STRUCTURE_DEFINITION_URL}/{profile}"])

    @staticmethod
    def get_bundle() -> Bundle:
        return Bundle(
            id=str(uuid4()),
            type="transaction",
            entry=[],
        )

    @staticmethod
    def get_organization(type) -> Organization:
        if type == "Collection":
            return Organization(
                id=ORGANIZATION_ID_COLL,
                meta=Meta(profile=[f"{BBMRI_STRUCTURE_DEFINITION_URL}/Collection"]),
                active=True,
                name=ORGANIZATION_NAME_COLL,
                alias=ORGANIZATION_ALIAS_COLL,
                partOf=Reference(reference=f"Organization/{ORGANIZATION_ID_BIO}"),
                contact=[
                    {
                        "address": Address(**contact["address"]),
                        "telecom": [
                            {
                                "system": item["system"],
                                "value": item["value"],
                                "use": item["use"],
                                "rank": item["rank"]
                            } for item in contact["telecom"]
                        ]
                    } for contact in ORGANIZATION_CONTACT_COLL
                ]
            )
        else:
            return Organization(
                id=ORGANIZATION_ID_BIO,
                meta=Meta(profile=[f"{BBMRI_STRUCTURE_DEFINITION_URL}/Biobank"]),
                active=True,
                name=ORGANIZATION_NAME_BIO,
                alias=ORGANIZATION_ALIAS_BIO,
                contact=[
                    {
                        "address": Address(**contact["address"]),
                        "telecom": [
                            {
                                "system": item["system"],
                                "value": item["value"],
                                "use": item["use"],
                                "rank": item["rank"]
                            } for item in contact["telecom"]
                        ]
                    } for contact in ORGANIZATION_CONTACT_BIO
                ]
            )

    @staticmethod
    def get_patient(
        id : str,
        sex: str,
        birthDate: Optional[date] = None,
        age: Optional[int] = None
        # age : int
    ) -> Patient:
       
        patient = Patient(
            id=id,
            gender=sex,
            birthDate=birthDate
        )
        
        # if age is provided instead of birthdate
        if age is not None:
            age_extension = Extension(
                url="http://example.org/fhir/StructureDefinition/age",
                valueAge=Age(
                    value=age,
                    unit="years",
                    system="http://unitsofmeasure.org",
                    code="a"
                )
            )
            patient.extension = [age_extension]
        # if birthDate:
        #     patient = Patient(
        #         id = id,
        #         gender=sex,
        #         birthDate=birthDate
        #         # age = age
        #     )
        # elif age:
        #     patient = Patient(
        #         id = id,
        #         gender=sex,
        #         # birthDate=birthDate
        #         age = age
        #     )
        # else:
        #     raise ValueError("Either birthDate or age must be provided")

        return patient

   
    
    def get_patient_ref(patient: Patient) -> Reference:
        return Reference(reference=f"{patient.resource_type}/{patient.id}")


    # https://samply.github.io/bbmri-fhir-ig/ValueSet-SampleMaterialType.html
    @staticmethod
    def get_material_type(    # da modificare. includere tutti i tipi di material type e il loro mapping
        material_type: models.SAMPLE_MATERIAL_TYPE_ENUM
        # material_preservation: models.SAMPLE_PRESERVATION_MODE_ENUM,
    ) -> Optional[CodeableConcept]:

        mat_type = material_type
        # mat_type = FHIRNormalization.get_material_type(
        #     material_type
        # )

        if mat_type:
            return CodeableConcept(
                coding=[Coding(code=mat_type, system=SAMPLE_MATERIAL_TYPE_SYSTEM)]
            )
        else:  # aggiunta
            log.critical(
                "Unknown Material Type: {}/{}", material_type
            )
        return None

    # Morphology to be converted in snomed? es:
    # https://phinvads.cdc.gov/vads/ViewCodeSystemConcept.action?oid=2.16.840.1.113883.6.96&code=403902008
    @staticmethod
    def get_diagnosis(      # da modificare. includere tutti le diagnosi e il loro mapping
        patient_ref: Reference,
        diagnosis: str,
        date_diagnosis: date, # non è possibile inserire sia l'età che la data
        age: int,
    ) -> Condition:

        diagnosis_code = diagnosis.split(" - ")[0]
        DIAGNOSIS = CodeableConcept(  # replaced CodeableConcept with CodeableReference
            coding=[
                Coding(
                    code=diagnosis_code, 
                    display=diagnosis_code,#display=diagnosis, 
                    system=ICD10_SYSTEM
                )
            ]
        )
   
        diagnosis_system = "http://terminology.hl7.org/CodeSystem/condition-ver-status"
        diagnosis_category = "http://terminology.hl7.org/CodeSystem/condition-category"


        # Inspired from:
        # https://www.hl7.org/fhir/condition-example-f202-malignancy.json.html
        return Condition(
            subject=patient_ref,
            # bodySite=[DIAGNOSIS],
            onsetDateTime=date_diagnosis,
            # onsetAge= AgeType(value = age, unit = "yr"),
            code=CodeableConcept(
                coding=[
                    Coding(
                        code=diagnosis_code,
                        display = diagnosis_code,
                        system=ICD10_SYSTEM,
                    )
                ]
            ), clinicalStatus=CodeableConcept(
                coding=[Coding(system="http://terminology.hl7.org/CodeSystem/condition-clinical", 
                               code="resolved")]
            ),
            verificationStatus=CodeableConcept(
                coding=[Coding(system=diagnosis_system, code="confirmed")]
            ),
            category=[
                CodeableConcept(
                    coding=[
                        Coding(system=diagnosis_category, code="encounter-diagnosis")
                    ]
                )
            ],
        )

   
    @staticmethod
    def get_specimen(
        id: str,
        patient_ref: Reference,
        diagnosis: str,
        collection_date: date,
        material_type: Optional[CodeableConcept],
        # surgery_start: Optional[date],
        temperature_room : Optional[int]
    ) -> Specimen:

        diagnosis_code = diagnosis.split(" - ")[0]
        DIAGNOSIS = CodeableConcept(
            coding=[
                Coding(
                    code=diagnosis_code, 
                    display=diagnosis_code,  #display=diagnosis, 
                    system=ICD10_SYSTEM
                )
            ]
        )

        return Specimen(
            extension=[
                Extension(
                    url=f"{BBMRI_STRUCTURE_DEFINITION_URL}/SampleDiagnosis",
                    valueCodeableConcept=CodeableConcept(
                        coding=[
                            Coding(
                                code=diagnosis_code,
                                display=diagnosis_code,#display=diagnosis,
                                system=ICD10_SYSTEM,
                            )
                        ]
                    ),
                ),
                Extension(
                    url=f"{BBMRI_STRUCTURE_DEFINITION_URL}/StorageTemperature",
                    valueCodeableConcept=CodeableConcept(
                        coding=[
                            Coding(
                                code=temperature_room,
                                display=temperature_room,
                                system=STORAGE_TEMPERATURE_SYSTEM,
                            )
                        ]
                    ),
                ),
                Extension(
                    url=f"{BBMRI_STRUCTURE_DEFINITION_URL}/Custodian",
                    valueReference=Reference(
                        reference=f"Organization/{ORGANIZATION_ID_COLL}"
                    ),
                ),
            ],
            status="available",
            type=material_type,
            subject=patient_ref,
            collection=SpecimenCollection(
                collectedDateTime=collection_date
            ),
        )

 