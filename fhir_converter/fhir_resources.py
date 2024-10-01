from datetime import date
from typing import List, Optional, Union
from uuid import uuid4
import yaml

import input_models as models
from loguru import logger as log
from normalization import FHIRNormalization

from fhir.resources.R4B.address import Address
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.codeablereference import CodeableReference
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.extension import Extension
from fhir.resources.R4B.fhirtypes import AgeType, String
from fhir.resources.R4B.medicationstatement import MedicationStatement
from fhir.resources.R4B.meta import Meta
from fhir.resources.R4B.observation import Observation
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.period import Period
from fhir.resources.R4B.procedure import Procedure
from fhir.resources.R4B.reference import Reference
from fhir.resources.R4B.specimen import Specimen, SpecimenCollection
from fhir.resources.R4B.age import Age



# load variables from configuration file
with open("biobank_config.yaml", "r") as file:
    config = yaml.safe_load(file)
locals().update(config)

ICD10_SYSTEM = "http://hl7.org/fhir/sid/icd-10"
SNOMED_SYSTEM = "http://snomed.info/sct"
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
    def get_organization(type: str) -> Organization:
        if type == "Biobank":
            return Organization(
                id=BIOBANK_ID,
                meta=Meta(profile=[f"{BBMRI_STRUCTURE_DEFINITION_URL}/Biobank"]),
                active=True,
                name=BIOBANK_NAME,
                alias=BIOBANK_ALIAS,
                identifier=[
                    {
                        "system": "http://www.bbmri-eric.eu/",
                        "value": BIOBANK_DIRECTORY_ID,
                    }
                ],
                address=[Address(
                            line = BIOBANK_LINE,
                            country=BIOBANK_COUNTRY,
                            city=BIOBANK_CITY,
                            postalCode=BIOBANK_POSTAL_CODE,
                        )],
                contact=[
                    {
                    "extension" : [
                        {
                        "url" : "https://fhir.bbmri.de/StructureDefinition/ContactRole",
                        "valueString" : "Director"
                        }
                    ],
                    "purpose" : {
                        "coding" : [
                        {
                            "system" : "http://terminology.hl7.org/CodeSystem/contactentity-type",
                            "code" : "ADMIN",
                            "display" : "Administrative"
                        }
                        ]
                    },
                    "name" : {
                        "family" : DIRECTOR_FAMILY_NAME,
                        "given" : DIRECTOR_GIVEN_NAME,
                        "prefix" : DIRECTOR_PREFIX_NAME
                    },
                    "telecom" : [
                        {
                        "system" : "phone",
                        "value" : DIRECTOR_PHONE
                        }
                    ]
                    },
                    {
                    "purpose" : {
                        "coding" : [
                        {
                            "system" : "https://fhir.bbmri.de/CodeSystem/ContactType",
                            "code" : "RESEARCH",
                            "display" : "Research"
                        }
                        ],
                        "text" : "Contact for research inquiries."
                    },
                    "name" : {
                        "family" : CONTACT_FAMILY_NAME,
                        "given" : CONTACT_GIVEN_NAME,
                        "suffix" : CONTACT_PREFIX_NAME
                    },
                    "telecom" : [
                        {
                        "system" : "phone",
                        "value" : CONTACT_PHONE
                        },
                        {
                        "system" : "email",
                        "value" : CONTACT_EMAIL
                        }
                    ],
                    "address" : {
                        "line" : CONTACT_ADD_LINE,
                        "city" : CONTACT_ADD_CITY,
                        "postalCode" : CONTACT_ADD_POSTAL_CODE,
                        "country" : CONTACT_ADD_COUNTRY
                    }
                    }
                ],
        
                    # first contact: Director
                #     {  "address": [Address(
                #             line = BIOBANK_LINE,
                #             country=BIOBANK_COUNTRY,
                #             city=BIOBANK_CITY,
                #             postalCode=BIOBANK_POSTAL_CODE,
                #         )],
                        
                #         "purpose": {
                #         "coding": [
                #             {
                #             "code": "RESEARCH",
                #             "display": "Research",
                #             "system": "https://fhir.bbmri.de/CodeSystem/ContactType"
                #             }]},
                #         "name": HumanName(
                #             family=BIOBANK_CONTACT_FAMILY,
                #             given=[BIOBANK_CONTACT_GIVEN],
                #             prefix=[BIOBANK_CONTACT_PREFIX],
                #         ),
                #         "telecom": [
                #             {"system": "phone", "value": CONTACT_PHONE},
                #             {"system": "email", "value": CONTACT_EMAIL},
                #         ],
                #     }
                # ],
                extension=[
                    {
                        "url": f"{BBMRI_STRUCTURE_DEFINITION_URL}/OrganizationDescription",
                        "valueString": BIOBANK_DESCRIPTION,
                    },
                    {
                        "url": f"{BBMRI_STRUCTURE_DEFINITION_URL}/JuridicalPerson",
                        "valueString": BIOBANK_JURIDICALPERSON,
                    },
                ],
            )
        else:
            return Organization(
                id=COLLECTION_ID,
                meta=Meta(profile=[f"{BBMRI_STRUCTURE_DEFINITION_URL}/Collection"]),
                active=True,
                identifier=[
                    {
                        "system": "http://www.bbmri-eric.eu/",
                        "value": COLLECTION_DIRECTORY_ID,
                    }
                ],
                name=COLLECTION_NAME,
                partOf=Reference(reference=f"Organization/{BIOBANK_ID}"),
                extension=[
                    {
                        "url": f"{BBMRI_STRUCTURE_DEFINITION_URL}/CollectionType",
                        "valueCodeableConcept": CodeableConcept(
                            coding=[
                                Coding(
                                    system="https://fhir.bbmri.de/CodeSystem/CollectionType",
                                    code=COLLECTION_TYPE_CODE,
                                )
                            ]
                        ),
                    },
                    {
                        "url": f"{BBMRI_STRUCTURE_DEFINITION_URL}/DataCategory",
                        "valueCodeableConcept": CodeableConcept(
                            coding=[
                                Coding(
                                    system="https://fhir.bbmri.de/CodeSystem/DataCategory",
                                    code=DATA_CATEGORY_CODE,
                                )
                            ]
                        ),
                    },
                    {
                        "url": f"{BBMRI_STRUCTURE_DEFINITION_URL}/OrganizationDescription",
                        "valueString": COLLECTION_DESCRIPTION,
                    },
                ],
            )

    @staticmethod
    def get_patient(
        id: str, sex: str, birthDate: Optional[date] = None, age: Optional[int] = None
    ) -> Patient:

        patient = Patient(id=id, gender=sex, birthDate=birthDate)

        if age is not None:
            patient.extension = [
                Extension(
                    url="http://example.org/fhir/StructureDefinition/age",
                    valueAge=Age(
                        value=age,
                        unit="years",
                        system="http://unitsofmeasure.org",
                        code="a",
                    ),
                )
            ]
        return patient

    @staticmethod
    def get_patient_ref(patient: Patient) -> Reference:
        return Reference(reference=f"{patient.resource_type}/{patient.id}")

    @staticmethod
    def get_material_type(
        material_type: models.MATERIAL_TYPE_ENUM,
    ) -> Optional[CodeableConcept]:
        if material_type:
            return CodeableConcept(
                coding=[Coding(code=material_type, system=SAMPLE_MATERIAL_TYPE_SYSTEM)]
            )
        else:
            log.critical("Unknown Material Type: {}/{}", material_type)
        return None

    @staticmethod
    def get_diagnosis(
        patient_ref: Reference,
        diagnosis: str,
        date_diagnosis: date,
        age: int,
    ) -> Condition:
        diagnosis_code = diagnosis.split(" - ")[0]
        DIAGNOSIS = CodeableConcept(
            coding=[Coding(code=diagnosis_code, system=ICD10_SYSTEM)]
        )

        diagnosis_system = "http://terminology.hl7.org/CodeSystem/condition-ver-status"
        diagnosis_category = "http://terminology.hl7.org/CodeSystem/condition-category"

        return Condition(
            subject=patient_ref,
            onsetDateTime=date_diagnosis,
            code=DIAGNOSIS,
            clinicalStatus=CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/condition-clinical",
                        code="resolved",
                    )
                ]
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
        storage_temp: Optional[int],
    ) -> Specimen:
        diagnosis_code = diagnosis.split(" - ")[0]
        DIAGNOSIS = CodeableConcept(
            coding=[Coding(code=diagnosis_code, system=ICD10_SYSTEM)]
        )

        return Specimen(
            id=id,
            extension=[
                Extension(
                    url=f"{BBMRI_STRUCTURE_DEFINITION_URL}/SampleDiagnosis",
                    valueCodeableConcept=DIAGNOSIS,
                ),
                Extension(
                    url=f"{BBMRI_STRUCTURE_DEFINITION_URL}/StorageTemperature",
                    valueCodeableConcept=CodeableConcept(
                        coding=[
                            Coding(
                                code=str(storage_temp),
                                system=STORAGE_TEMPERATURE_SYSTEM,
                            )
                        ]
                    ),
                ),
                Extension(
                    url=f"{BBMRI_STRUCTURE_DEFINITION_URL}/Custodian",
                    valueReference=Reference(reference=f"Organization/{COLLECTION_ID}"),
                ),
            ],
            status="available",
            type=material_type,
            subject=patient_ref,
            collection=SpecimenCollection(collectedDateTime=collection_date),
        )
