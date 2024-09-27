from datetime import date
from typing import List, Optional, Union
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
from fhir.resources.fhirtypes import AgeType, String
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.meta import Meta
from fhir.resources.observation import Observation
from fhir.resources.organization import Organization
from fhir.resources.humanname import HumanName
from fhir.resources.patient import Patient
from fhir.resources.period import Period
from fhir.resources.procedure import Procedure
from fhir.resources.reference import Reference
from fhir.resources.specimen import Specimen, SpecimenCollection
from fhir.resources.age import Age

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
                contact=[
                    {
                        "address": Address(
                            country=BIOBANK_COUNTRY,
                            city=BIOBANK_CITY,
                            postalCode=BIOBANK_POSTAL_CODE,
                        ),
                        "telecom": [
                            {"system": "phone", "value": CONTACT_PHONE},
                            {"system": "email", "value": CONTACT_EMAIL},
                        ],
                    }
                ],
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
