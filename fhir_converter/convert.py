import sys
from pathlib import Path
from typing import Dict
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
from tqdm import tqdm


"""
conversion.py -----------------------------------------------------------------
overall wrapper, takes as input one excel (classic dataset table) written in 
the BBMRI appendix format and creates the FHIR-structured JSON to be uploaded 
on the Biobank Locator.
-------------------------------------------------------------------------------
"""


app = typer.Typer()

log.remove()
log.add(
    sys.stderr,
    format="<level>{time:YYYY-MM-DD HH:mm:ss}</level> | <level>{level}</level> | <black>{message}</black>",
    colorize=True,
)
@app.command()
def convert(
    filename: Path = typer.Option(..., help="Path of input file"),
    outdir: Path = typer.Option(..., help="Path of output folder"),
    miabis: bool = typer.Option(default= False, help= "Flag for MIABIS normalization"),
    colnames: bool = typer.Option(default= False, help= "Flag for colnames"),

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

    # create a bundle with collection resource and biobank resource
    bundle = FHIRResources.get_bundle()

    biobank = FHIRResources.get_organization("Biobank")
    collection = FHIRResources.get_organization("Collection")
    bundle.entry.append(biobank)
    bundle.entry.append(collection)
    bundle_data = bundle.dict()
    bundle_data = bbmri_post_serialization(bundle_data)

    ## create a json file for the organization
    with open(f"{outdir}/organization.json", "w") as f:
        json.dump(bundle_data, f, default=str, indent=4)

    for ws in wb.worksheets:
        if ws.sheet_state == "hidden":
            log.warning("Ignoring hidden sheet: {}", ws.title)
            continue

        # log.info("Reading sheet {}", ws.title)

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
        counters: Dict[str, int] = {}
        ## for each cell, take the value and put it in patient_data dict with key = header
        # for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=len(header)):
        total_rows = 0
        valid_rows = 0
        invalid_rows = 0
        missing_fields_count = 0

        
        for row_number, row in tqdm(
            enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=len(header)), start=2),
            total=wb.active.max_row-1):

            if ws.row_dimensions[row_number].hidden: # if the row is hidden: skip
                continue

            # total_rows += 1
            patient_data: Dict[str, str] = {}

            for cell in row:
                patient_data[header[cell.col_idx - 1]] = cell.value

            if all(value is None for value in patient_data.values()):
            # if all the fields are None --> stop (no more rows)
                break

            if not miabis:  # if not MIABIS-compliant   
                patient_data = normalize_input(patient_data, "mapping_config.yml")
            if colnames:    # if MIABIS-compliant but with different field names
                patient_data = normalize_input(patient_data, "mapping_config.yml", colnames  = True)
 
            try:
                patient = PatientInputModel(**patient_data)
            except ValidationError as e:
                invalid_rows += 1
                sample_id = patient_data.get("SAMPLE_ID", "UNKNOWN")

                # Check missing mandatory fields
                has_missing_fields = any(error["msg"] == "field required" for error in e.errors())
                if has_missing_fields:
                    missing_fields_count += 1  

                print("\n")
                log.error("Error in row {} (SAMPLE_ID: {})\n-----------------------------", row_number-1, sample_id)

                for error in e.errors():
                    field = error["loc"][0]
                    error_message = error["msg"]
                    received_value = patient_data.get(field, "N/A")

                    if error_message == "field required":
                        log.error("❌ Missing required field: {}", field)
                   
                    else:
                        # Show admitted values
                        allowed_values = error["ctx"].get("enum_values") if "ctx" in error and "enum_values" in error["ctx"] else None
                        if allowed_values:
                            log.error("🚫  Invalid value for field: {} | Value received: [{}]\nAllowed values: {}", 
                                    field, received_value, allowed_values)
                        elif error_message == "DIAGNOSIS must be a valid ICD-10 code":
                             log.error("🚫  Invalid ICD-10 code: {} | Value received: [{}]", 
                                    field, received_value)
                        else:
                            pass

                log.error("==============================================\n")
                                        
            else:
                valid_rows += 1
                patient = normalize_output(patient)
                patient_serializer = FHIRSerializer(patient, counters)

                pat_id = patient_serializer.PATIENT_ID
                copy = pat_id in patients_ids
                patients_ids.append(pat_id)

                sample_id, bundle = patient_serializer.serialize_patient(bundle, copy)
                bundle_data = bundle.dict()
                bundle_data = bbmri_post_serialization(bundle_data)

                with open(f"{outdir}/bundle-{bundle.id}.json", "w") as f:
                    json.dump(bundle_data, f, default=str, indent=4)
            total_rows += 1
            
        # Final report with invalid rows
        print("\nData Quality Report:")
        log.info(f"Total Processed Rows: {total_rows}")
        log.info(f"Valid Rows: {valid_rows}")
        log.info(f"Invalid Rows: {invalid_rows}")
        log.info(f"Total Rows with Missing Fields {missing_fields_count}")

        if invalid_rows == 0:
            log.success("Conversion completed successfully!")
            print(f"Conversion completed successfully! Bundles generated in {outdir} folder.")
        else:
            log.warning(f"Process completed with {invalid_rows} errors!")
            print(f"Process completed with {invalid_rows} errors. Check the logs for more details.")

        # Parse the first sheet only
        break
    

if __name__ == "__main__":
    app()


