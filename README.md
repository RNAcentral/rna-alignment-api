# RNA Alignment API

A Flask API for serving RNA multiple sequence alignment data from Stockholm files stored in S3.

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with your S3 credentials:

```
S3_HOST=https://uk1s3.embassy.ebi.ac.uk
S3_KEY=your_access_key
S3_SECRET=your_secret_key
BUCKET_NAME=ebi-rnacentral
ENVIRONMENT=dev
S3_BASE_PATH=alignments
```

The API expects Stockholm files to be stored in the S3 bucket `ebi-rnacentral` under the path `dev/alignments/`.

## Usage

Start the server:

```bash
python app.py
```

The API will run on `http://localhost:5000` by default.

## API Endpoints

### Get RNA Alignment Sequences

- **URL:** `/{identifier}`
- **Method:** GET
- **Description:** Returns RNA sequences in MSA component format
- **Example:** `GET /RF03116`


## Example Response

```json
{
  "status": "success",
  "data": {
    "consensus": "ccc.gcc..cggGU.CUGUGGuuGaA.................................................................................AGUCgAcGcC.agccGcgGgCa.AAacGAuCCAcgUAacccccca............................aaaau................................................................................................gggggguGAccAUGgcgCggc....................................uUAGAaGUA.AGuC.cug.C.Cgccc..............................aaaaa...............................................................................................gggcGAGAGgg.cua.gUA..guGagg.ggcaaaa............................................................gccuauuA...gcgAAagccCCa..Gcag.....GCGAGU.gUGGG.GuCAAA.aaCCAG.GUCAGccg..g.gcggg",
    "identifier": "RF03072",
    "notation": {
      "basePairs": [
        {"score": 1, "x": 316, "y": 327},
        {"score": 1, "x": 151, "y": 682}
      ],
      "consensus": "[[[.[[[..[[[--.[[[[[[[[---................................................................................."
    },
    "sequences": [
      {
        "name": "URS0000D6BF59_12908/1-314",
        "sequence": "GAA-CGC--CCGGU-CUGUCGGUGAA---------------------------------------------------------------------------------AAGCGAUGCG-AGACCGGCGCG-AAACGCUCUCAGUAAUCCUCCGcacuccgg--------------------UCCGCuuagcacggaguccgagaguggcagagcuccguaaauucggaguucgcuauucgaccacaugc-------------------------ucgga---AGGAGGAGAUCAUGGCCGGGCcggccugggcugccgaagcucagcagcucugaagucCUUUGUGUA-AGUC-GCG-C-CGCC------------------------
```

## S3 File Structure

The API expects files to be organized as follows, with the SEED files containing the Stockholm data:

```
ebi-rnacentral/
└── dev/
    └── alignments/
        ├── RF00001/
            └── SEED
        ├── RF00002/
            └── SEED
```


## Docker and Kubernetes

The code is Dockerized and can be deployed on a kubernetes cluster with secrets for S3_HOST, S3_KEY and S3_SECRET. The Dockerfile can be built and pushed with:

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/rnacentral/rna-alignment-api:latest --push .
```
It can then be deployed with:

```bash
cd kubernetes/helm
helm install rna-alignment-api-full . -n rna-alignment  
```