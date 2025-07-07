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
```

The API expects Stockholm files to be stored in the S3 bucket `ebi-rnacentral` under the path `dev/alignments/`.

## Usage

Start the server:

```bash
python app.py
```

The API will run on `http://localhost:5000` by default.

## API Endpoints

### Get RNA Family Sequences

- **URL:** `/family/{identifier}`
- **Method:** GET
- **Description:** Returns RNA sequences in MSA component format
- **Example:** `GET /family/RF03116`
- **Note:** The identifier is converted to lowercase when fetching from S3 (e.g., `RF03116` → `rf03116.sto`)

### Get Raw Sequences

- **URL:** `/family/{identifier}/raw`
- **Method:** GET
- **Description:** Returns sequences in raw JSON format
- **Example:** `GET /family/RF03116/raw`

### Health Check

- **URL:** `/health`
- **Method:** GET
- **Description:** Check if the API is running

### Home

- **URL:** `/`
- **Method:** GET
- **Description:** API information and usage examples

## Environment Variables

- `PORT`: Server port (default: 5000)
- `DEBUG`: Enable debug mode (default: False)
- `S3_HOST`: S3 endpoint URL
- `S3_KEY`: S3 access key
- `S3_SECRET`: S3 secret key

## Dependencies

- Flask
- Flask-CORS
- Biopython
- boto3
- python-dotenv

## Example Response

```json
{
  "status": "success",
  "data": {
    "sequences": [
      {
        "name": "sequence_id",
        "sequence": "ACGTACGT..."
      }
    ],
    "metadata": {
      "title": "RF03116 RNA Family",
      "description": "Multiple sequence alignment for RNA family RF03116",
      "source": "S3: ebi-rnacentral/dev/alignments/rf03116.sto",
      "count": 42,
      "identifier": "RF03116"
    }
  },
  "message": "Data loaded successfully"
}
```

## S3 File Structure

The API expects files to be organized as follows:

```
ebi-rnacentral/
└── dev/
    └── alignments/
        ├── rf03116.sto
        ├── rf00001.sto
        └── ...
```

Stockholm files should be in lowercase and follow the naming convention `{identifier}.sto`.