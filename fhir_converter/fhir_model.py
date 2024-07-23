from typing import Any, Dict, Optional, Tuple
import yaml
import input_models as models
from fhir_resources import FHIRResources
from loguru import logger as log
from normalization import FHIRNormalization

from fhir.resources.bundle import Bundle
from fhir.resources.resource import Resource


with open("general_config.yaml", "r") as config_file:
    config_data = yaml.safe_load(config_file)
SERVER_URL = config_data.get("server_url", "")

class FHIRSerializer:
    def __init__(self, input_patient: models.Patient, counters) -> None:
        self.counters = counters
        self.input_patient = input_patient
        
        # We decided to use the SAMPLE_ID as PATIENT_ID
        # SAMPLE_ID will be assigned as PATIENT_ID-specimen-0
        self.PATIENT_ID = self.input_patient.PATIENT_ID
        self.SAMPLE_ID = self.input_patient.SAMPLE_ID

        # Underscore is not allowed in IDs, converting _ to -
        if "_" in self.PATIENT_ID:
            self.PATIENT_ID = self.PATIENT_ID.replace("_", "-")

        self.DIAGNOSIS = FHIRNormalization.get_diagnosis_icd10(
            self.input_patient.DIAGNOSIS
        )

        self.MATERIAL_TYPE = FHIRResources.get_material_type(self.input_patient.MATERIAL_TYPE)

  

    def add_to_bundle(
        self,
        bundle: Bundle,
        resource: Resource,
        resource_id: Optional[str] = None,
        patient_id: Optional[str] = None,
    ) -> None:
        resource.meta = FHIRResources.get_meta(resource.resource_type)
    

        if resource_id:
            # resource_id = resource_id.replace("-", "").replace(" ","")
            resource.id = resource_id
        elif patient_id:
            # patient_id = patient_id.replace("-", "").replace(" ","")
            resource.id = self.generate_id(patient_id, resource.resource_type)
            # resource.id = self.input_patient.SAMPLE_ID.replace("-", "").replace(" ","")

        bundle.entry.append(resource)

    def generate_id(self, patient_id: str, resource_type: str) -> str:
        counter = self.counters.get(patient_id+resource_type, 0)
        self.counters[patient_id+resource_type] = counter + 1
        return f"{patient_id}-{resource_type.lower()}-{counter}"

    def serialize_patient(self, bundle, copy) -> Tuple[str, Bundle]:

        # bundle = FHIRResources.get_bundle() -> rimosso per avere un singolo bundle

        # ##############################################
        # ################   Patient   #################
        # ##############################################
        if self.input_patient.BIRTH_DATE:
            patient = FHIRResources.get_patient(
                id = self.PATIENT_ID,
                sex=self.input_patient.SEX,
                # age=self.input_patient.AGE
                birthDate=self.input_patient.BIRTH_DATE
            )
        else:
            patient = FHIRResources.get_patient(
                id = self.PATIENT_ID,
                sex=self.input_patient.SEX,
                age=self.input_patient.DONOR_AGE
                # birthDate=self.input_patient.BIRTH_DATE
            )
        if not copy: self.add_to_bundle(bundle, patient, resource_id=self.PATIENT_ID)

        patient_ref = FHIRResources.get_patient_ref(patient)


        # #################################################
        # ################ Main Diagnosis #################
        # #################################################

        diagnosis = FHIRResources.get_diagnosis(
            patient_ref=patient_ref,
            diagnosis=self.input_patient.DIAGNOSIS,
            # hist_morphology=self.input_patient.HIST_MORPHOLOGY,
            date_diagnosis=self.input_patient.DATE_DIAGNOSIS,
            age=self.input_patient.AGE_AT_PRIMARY_DIAGNOSIS,
        )

        # if the patient has been added yet-- > no duplicate diagnosis
        if not copy: self.add_to_bundle(bundle, diagnosis, patient_id=self.PATIENT_ID)


        # ##############################################
        # ################  Specimen   #################
        # ##############################################
        specimen = FHIRResources.get_specimen(
            id = self.SAMPLE_ID,
            patient_ref=patient_ref,
            diagnosis=self.input_patient.DIAGNOSIS,
            collection_date=self.input_patient.SAMPLING_DATE,
            material_type=self.MATERIAL_TYPE,
            temperature_room=self.input_patient.STORAGE_TEMPERATURE
            # surgery_start=self.SURGERY_START,
        )
        self.add_to_bundle(bundle, specimen, patient_id=self.PATIENT_ID, resource_id=self.SAMPLE_ID)


        return self.PATIENT_ID, bundle
      

# Extend dict with FHIR unsupported fields like fullUrl and request
# Each resource should be grouped in a bundle?
# but the ORM seems to not support resource field (only entry field)
# and type is mandatory (but missing in their example)
# so... let's bypass everything and manipulate the output...
def bbmri_post_serialization(bundle: Dict[str, Any]) -> Dict[str, Any]:

    if "entry" not in bundle:
        log.warning("Malformed bundle, entry key not found")
        return bundle

    for key, entry in enumerate(bundle["entry"]):

        if "resourceType" not in entry:
            log.warning("Malformed bundle, resourceType key not found in {}", entry)
            continue

        if "id" not in entry:
            log.warning("Malformed bundle, id key not found in {}", entry)
            continue

        resource = entry["resourceType"]
        _id = entry["id"]

        bundle["entry"][key] = {
            "fullUrl": f"{SERVER_URL}/{resource}/{_id}",
            "request": {"method": "PUT", "url": f"{resource}/{_id}"},
            "resource": entry,
        }
    return bundle
