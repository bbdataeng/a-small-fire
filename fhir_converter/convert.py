
# py convert.py --filename "C:\\Users\\Antonella\\Desktop\\FHIR\\sample-colon-dataset.xlsx" --outdir "C:\\Users\\Antonella\\Desktop\\FHIR"
import sys
from pathlib import Path
from typing import Dict
import os
import simplejson as json  # base json is unable to properly serialize Decimals
import typer
from fhir_model import FHIRSerializer, bbmri_post_serialization
from fhir_resources import FHIRResources
from input_models import Patient as PatientInputModel
from loguru import logger as log
from normalization import normalize_input, normalize_output
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from pydantic import ValidationError


"""
conversion.py -----------------------------------------------------------------
overall wrapper, takes as input one excel (classic dataset table) written in 
the BBMRI appendix format and creates the FHIR-structured JSON to be uploaded 
on the Biobank Locator

-------------------------------------------------------------------------------

Questo modello ridotto utilizza soltanto i seguenti campi:
    # ########## Donor/Clinical Information
    # Patient pseudonym
    PATIENT_ID: Optional[str]
    # Age at diagnosis (rounded to years)
    AGE_AT_PRIMARY_DIAGNOSIS: int
    # Biological sex
    SEX: SEX_ENUM
    # Date of diagnosis
    DATE_DIAGNOSIS: date
    # Diagnosis (ICD-10)
    DIAGNOSIS : DIAGNOSIS_ENUM
    # Donor Age / Date of birth
    DONOR_AGE : date
    # AGE: int

    # ########## Sample
    # Sample ID
    SAMPLE_ID: str
    # Material type
    SAMPLE_MATERIAL_TYPE: SAMPLE_MATERIAL_TYPE_ENUM
    # Year of sample collection
    YEAR_OF_SAMPLE_COLLECTION: int
    # Room temperature
    ROOM_TEMPERATURE: Optional[str]

"""


app = typer.Typer()


@app.command()
def convert(
    filename: Path = typer.Option(..., help="Path of input file"),
    outdir: Path = typer.Option(..., help="Path of output folder"),
) -> None:

    if not filename.exists():
        sys.exit(f"ERROR: File '{filename}' does not exist")

    if not outdir.exists():
        sys.exit(f"ERROR: Outdir '{outdir}' does not exist")

    try:
        wb = load_workbook(filename=filename)
    except InvalidFileException as e:
        sys.exit(str(e))

    header: Dict[int, str] = {}

    ## create empty bundle
    bundle = FHIRResources.get_bundle()
    ## add organization 
    organization = FHIRResources.get_organization()
    bundle.entry.append(organization)
    bundle_data = bundle.dict()
    bundle_data = bbmri_post_serialization(bundle_data)

    # counters = {}

    ## create a json file for the organization
    with open(f"{outdir}/organization.json", "w") as f:
        json.dump(bundle_data, f, default=str, indent=4)


    for ws in wb.worksheets:
        if ws.sheet_state == "hidden":
            log.warning("Ignoring hidden sheet: {}", ws.title)
            continue

        log.info("Reading sheet {}", ws.title)

        ## create header
        ## for each cell save the value (header name), until None (columns end)
        for row in ws.iter_rows(min_row=1, max_row=1, max_col=999):
                for cell in row:
                    if cell.value is None:
                        break
                    header[cell.col_idx - 1] = cell.value

        ## CREATE PATIENT DATA
        bundle = FHIRResources.get_bundle()
        patients_ids = []
        ## for each cell, take the value and put it in patient_data dict with key = header
        # for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=len(header)):
        for row_number, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=len(header)), start=2):
            if ws.row_dimensions[row_number].hidden: # if the row is hidden, skip it
                continue 

            patient_data: Dict[str, str] = {}

            for cell in row:
                patient_data[header[cell.col_idx -1]] = cell.value

            if all(value is None for value in patient_data.values()): # if all the fields are None --> stop (no more rows)
                break
            patient_data = normalize_input(patient_data)

            try:
                ## Create Patient Resource with patient_data
                ## validation of fields with pydantic
                patient = PatientInputModel(**patient_data)
            except ValidationError as e:
                print(e)

                for field in str(e).split("\n")[1::2]:
                    log.error(
                        "{}: {} = [{}]",
                        patient_data.get("SAMPLE_ID", ""),
                        field,
                        patient_data.get(field, "N/A"),
                    )
            else:
                patient = normalize_output(patient) # another mapping 
                print("PATIENT\n", patient)
                patient_serializer = FHIRSerializer(patient)

                pat_id = patient_serializer.PATIENT_ID
                copy = pat_id in patients_ids
                patients_ids.append(pat_id)
                ## una lista che tiene traccia dei pazienti già inseriti nel bundle (poco efficiente?)
                ## creando un bundle per ogni paziente il bridgehead lo accetta?

                # sample_id, bundle = patient_serializer.serialize_patient()
                # bundle_data = bundle.dict()
                # bundle_data = bbmri_post_serialization(bundle_data)

                # # appending?
                # # problema: aggiunge un bundle per ogni specimen
                # with open(f"{outdir}/{sample_id}.json", "a+") as f: 
                #     json.dump(bundle_data, f, default=str, indent=4)

                # patient_id history
                # counter = counters.get(patient_data['PATIENT_ID'], 0)
                # counters[patient_data['PATIENT_ID']] = counter + 1
                # with open(f"{outdir}/{sample_id}-{counter}.json", "w") as f: 
                #     json.dump(bundle_data, f, default=str, indent=4)
                
            
                sample_id, bundle = patient_serializer.serialize_patient(bundle, copy)
                bundle_data = bundle.dict()
                bundle_data = bbmri_post_serialization(bundle_data)

                with open(f"{outdir}/bundle-{bundle.id}.json", "w") as f: 
                    json.dump(bundle_data, f, default=str, indent=4)
                

        # Parse the first sheet only
        break


if __name__ == "__main__":
    app()
