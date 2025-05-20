# a-small-fire

**a-small-fire** is a toolkit developed by the BBMRI.it Data Engineering team to facilitate the transformation step of the ETL (Extract, Transform, Load) process, converting datasets into the HL7 FHIR® (Fast Healthcare Interoperability Resources) standard.

The toolkit is built on the open-source [FHIR Resources](https://github.com/nazrulworld/fhir.resources) library.

![workflow](https://github.com/bbdataeng/a-small-fire/blob/version4/figures/graphical-abstract.png)

---

## Input Data Requirements

Your input dataset should include the following **essential fields**:

- **Sampling Date**
- **Donor Birth Date**
- **Diagnosis Age Donor**
- **Gender**
- **Date of Diagnosis**
- **Diagnosis ICD-10**
- **Sample Type**
- **Storage Temperature**

In addition, the dataset must include unique identifiers for both the patient and the sample:

- **Patient_ID**
- **Sample_ID**

## Data Formats

## Data Format Notes

Data should follow the **[MIABIS](https://github.com/BBMRI-ERIC/miabis/tree/5a478a90ad31bc0164d76566ee3d948c76a925a6) Common Data Model**.  
If your dataset does not use MIABIS-standard, please define your own mappings in `mapping_config.yml`.

| Field                    | Expected Format                             | Notes                                                                 |
|--------------------------|---------------------------------------------|-----------------------------------------------------------------------|
| **SAMPLING_DATE**        | `YYYY-MM-DD`                                |                                                                      |
| **BIRTH_DATE**     | `YYYY-MM-DD` or partial (`YYYY`)            | If only a 4-digit year is provided, it will be interpreted as `YYYY-01-01` |
| **DIAGNOSIS_AGE**  | Integer (e.g., `45`)                        |                                                                      |
| **SEX**               | MIABIS vocabulary   |                                                                      |
| **DIAGNOSIS_DATE**    | `YYYY-MM-DD`                                |                                                                      |
| **DIAGNOSIS**     | Valid ICD-10 code (e.g., `C50.9`)           |                                                                      |
| **MATERIAL_TYPE**          | MIABIS vocabulary                           |                                                                      |
| **STORAGE_TEMPERATURE**  | MIABIS vocabulary                                  |                                                                      |
| **PATIENT_ID**, **SAMPLE_ID** | Unique alphanumeric strings            |                                                                      |

---

## Key Modules

The toolkit is structured into several key modules:

### Conversion
   - The core module of the toolkit.
   - Takes an Excel file as input and generates a FHIR-structured JSON file ready for upload to the Biobank FHIR Store.

### Normalization
   - Maps dataset fields that do not follow the MIABIS standard into MIABIS-compliant fields.

### Input-Model
   - Contains all valid input values, which are used to validate and normalize data based on the MIABIS Common Data Model (CDM).

### FHIR-Model
   - A high-level converter that transforms the input dataset into the FHIR format, following the [BBMRI.de implementation guide](https://samply.github.io/bbmri-fhir-ig/).

### FHIR-Resources
   - This module is responsible for mapping each field in the dataset to its appropriate FHIR Resource.

---

## Installation and Setup

To get started with the toolkit, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/bbdataeng/a-small-fire.git
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### Usage

The toolkit offers two main options depending on whether your input data already conforms to the [MIABIS](https://github.com/BBMRI-ERIC/miabis) standard:


#### 1. Input Data in MIABIS Standard

If your input data already follows the MIABIS standard, you can use the `--miabis` flag for quicker conversion:

```bash
cd fhir_converter
python convert.py --filename <INPUT_DATA> --outdir "../output" --miabis  
```

#### 2. Input Data Not in MIABIS Standard

If your input data is not in the MIABIS standard, you’ll need to edit the `mapping_config.yml` file to map your local data fields into MIABIS CDM fields. After editing the mapping configuration, run the following command:

```bash
cd fhir_converter
python convert.py --filename <INPUT_DATA> --outdir "../output"   
```



---

### Configuration Files
There are two main configuration files:

- `biobank_config.yml:`
        Stores general configuration information, such as organization ID, collection ID, and the Biobank Locator server URL.

- `mapping_config.yml:`
        Defines how to map the fields in your local dataset to MIABIS CDM fields if your data is not already standardized.


---

### Output

Two json files are generated from this tool:

- `bundle-<BUNDLE_ID>.json:`
        Stores a transaction bundle with Patient and Specimen FHIR Resources.

- `organization.json:`
        Stores a transaction bundle with Organization/Biobank and Organization/Collection FHIR Resources.

--- 

### Additional Resources

For more information on the MIABIS standard and a sample dataset template, check out the [minimum-dataset-template](https://github.com/bbdataeng/a-small-fire/blob/version4/extra/minimal-dataset-template.xlsx).