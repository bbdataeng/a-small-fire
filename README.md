# FHIR converter

FHIR converter/Transformer “toolkit” developed by the BBMRI-IT team to support the Transform step of the ETL process. 

The toolkit is based on the open source FHIR RESOURCES library available at https://github.com/nazrulworld/fhir.resources.

<!-- The toolkit uses the [CRC-ADOPT](https://ec.europa.eu/research/participants/documents/downloadPublic?documentIds=080166e5c9716d4e&appId=PPGMS) common data model. -->

![workflow](https://github.com/antocruo/bbdataeng/a-small-fhir/extra/graphical_abstract.png)


## Basic Model - a small FHIR

Minimal denominators' findable in the Federated Platform tools:  

* Donor/Clinical Information
    - Patient_ID
    - Gender                  
    - Diagnose ICD-10
    - Diagnosis age donor 
    - Date of diagnosis


* Sample
    - Sample_ID
    - Donor Age
    - Sample Type             
    - Sampling date 
    - StorageTemperature     

## Modules

The main modules of the converter are: 

<img src="https://github.com/antocruo/bbdataeng/assets/51079644/1e590644-4a46-48ba-9331-2499c8725259" width="500" height="500"/>

**Conversion:** overall wrapper, takes as input one excel (classic dataset table) written in the BBMRI appendix format and creates the FHIR-structured JSON to be uploaded on the Biobank Locator. 

**Configuration:** contains a series of configuration values such as the organization id and the locator URL

**Normalization:** the normalization module maps many non-compliant fields to a series of normalized fields, for instance patient.SEX to M; F; other; unknown; 

**INPUT-MODELS:** contains all the possible values for the input employed in the validation and normalization process.

The FHIR final JSON is built by two separate modules: 

**FHIR-MODEL:** this module is the high-level converter from the dataset to the FHIR  

**FHIR-RESOURCES:** is employed by the FHIR-MODEL module and maps each field / entity to its FHIR counterpart 

## Requirements
``` shell
pip install -r fhir_converter/requirements.txt
```

<!-- Mandatory colnames:

-SEX

-DIAGNOSIS

-DATE_DIAGNOSIS

-DOB

-YEAR_OF_SAMPLE_COLLECTION

-SAMPLE_MATERIAL_TYPE

-STORAGE_TEMPERATURE

-PATIENT_ID

-SAMPLE_ID -->


## Usage
``` shell
cd fhir_converter
convert.py --filename "../fhir/data/<.xlsx FILENAME>" --outdir "../fhir/output"
```

## Output

* `organization.json`: information about the resource Organization

<!-- * `test{patient_ID}SAMPLE.json`: information about the resource Patient -->
* `bundle-<BUNDLE_ID>.json`: bundle with all the Resources in the .xlsx file 



