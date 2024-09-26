# a-small-fire

**a-small-fire** is a toolkit developed by the BBMRI.it Data Engineering team to facilitate the transformation step of the ETL (Extract, Transform, Load) process, converting datasets into the FHIR® (Fast Healthcare Interoperability Resources) format.

The toolkit is built on the open-source [FHIR RESOURCES](https://github.com/nazrulworld/fhir.resources) library.

![workflow](https://github.com/bbdataeng/a-small-fhir/blob/simpler-fhir/figures/asmallfire.png)

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

---

## Key Modules

The toolkit is structured into several key modules to handle different parts of the transformation process:

### 1. **Conversion**
   - The core module of the toolkit.
   - Takes an Excel file (containing dataset tables) as input and generates a FHIR-structured JSON file ready for upload to the Biobank FHIR Store.

### 2. **Configuration**
   - Manages various configuration settings, such as the organization ID and Biobank Locator URL.

### 3. **Normalization**
   - Maps dataset fields that do not follow the MIABIS standard into MIABIS-compliant fields.

### 4. **Input-Model**
   - Contains all valid input values, which are used to validate and normalize data based on the MIABIS Common Data Model (CDM).

### 5. **FHIR-Model**
   - A high-level converter that transforms the input dataset into the FHIR format, following the [BBMRI.de implementation guide](https://samply.github.io/bbmri-fhir-ig/).

### 6. **FHIR-Resources**
   - This module is responsible for mapping each field or entity in the dataset to its appropriate FHIR structure, helping to ensure compatibility with FHIR standards.

---

## Installation and Setup

To get started with the toolkit, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/bbdataeng/a-small-fire.git
```

### 2. Install dependencies

Install the required dependencies by running the following command:

```bash
pip install -r requirements.txt
```

---

### Usage
The toolkit offers two main options depending on whether your input data already conforms to the MIABIS standard:


#### 1. Input Data in MIABIS Standard

If your input data already follows the MIABIS standard, you can use the `--miabis` flag for quicker conversion:

```bash
cd fhir_converter
py convert.py --filename <INPUT_DATA> --outdir "../output" --miabis  
```

#### 2. Input Data Not in MIABIS Standard

If your input data is not in the MIABIS standard, you’ll need to edit the `mapping_config.yml` file to map your local data fields into MIABIS CDM fields. After editing the mapping configuration, run the following command:

```bash
cd fhir_converter
py convert.py --filename <INPUT_DATA> --outdir "../output"   
```

---

### Configuration Files
There are two main configuration files that are critical for the toolkit:

- `biobank_config.yml:`
        Stores general configuration information, such as organization ID, collection ID, and the Biobank Locator server URL.

- `mapping_config.yml:`
        Defines how to map the fields in your local dataset to MIABIS CDM fields if your data is not already standardized.


### Additional Resources

For more information on the MIABIS standard and a sample dataset template, check out the [minimum-dataset-template](https://github.com/bbdataeng/a-small-fhir/blob/simpler-fhir/extra/minimum-dataset-template.xlsx).