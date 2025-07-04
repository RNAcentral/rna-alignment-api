# RNA Alignment API

A simple Flask API for serving RNA multiple sequence alignment data from Stockholm files.

## Installation

Install dependencies:

```bash
pip install flask flask-cors
```

Make sure you have a Stockholm file (`rf03116.sto`) and the `sto_parser` module in your project directory.

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

### Get Raw Sequences

- **URL:** `/family/{identifier}/raw`
- **Method:** GET
- **Description:** Returns sequences in raw JSON format
- **Example:** `GET /family/RF03116/raw`

### Health Check

- **URL:** `/health`
- **Method:** GET
- **Description:** Check if the API is running and how many sequences are loaded

### Home

- **URL:** `/`
- **Method:** GET
- **Description:** API information and usage examples

## Configuration

Set environment variables:

- `PORT`: Server port (default: 5000)
- `DEBUG`: Enable debug mode (default: False)

## Example Response

```json
{
  "status": "success",
  "data": {
    "sequences": [...],
    "metadata": {
      "title": "RF03116 RNA Family",
      "description": "Multiple sequence alignment for RNA family RF03116",
      "source": "Stockholm file: rf03116.sto",
      "count": 42,
      "identifier": "RF03116"
    }
  },
  "message": "Data loaded successfully"
}
```