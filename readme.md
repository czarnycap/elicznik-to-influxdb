# elicznik-to-influxdb

A Python script to import energy usage data from `.dat` files into InfluxDB, and to fetch or test the connection to your InfluxDB instance.

## Features

- **Push data** from `.dat` files to InfluxDB
- **Fetch data** from InfluxDB for a given time range
- **Test connection** to InfluxDB

## Requirements

- Python 3.7+
- InfluxDB (tested with 1.x)
- Python packages: `influxdb`, `python-dotenv`

## Installation

1. **Clone the repository:**
   ```bash
   git clone git@github.com:czarnycap/elicznik-to-influxdb.git
   cd elicznik-to-influxdb
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install influxdb python-dotenv
   ```

4. **Prepare your `.env` file:**

   Create a `.env` file in the project directory with the following content (adjust as needed):

   ```
   INFLUXDB_HOST=localhost
   INFLUXDB_PORT=8086
   INFLUXDB_DATABASE=your_database
   INFLUXDB_USER=your_user
   INFLUXDB_PASSWORD=your_password
   INPUT_FOLDER=./data
   ```

5. **Prepare your data:**

   Place your `.dat` files in the folder specified by `INPUT_FOLDER` (default: `./data`).  
   Each `.dat` file should have lines like:
   ```
   2024-12-31T00:00:00,0.251,0.0,,
   ```

## Usage

Run the script with one of the following options:

### Test InfluxDB Connection

```bash
python push_to_influxdb.py --test-connection
```

### Push Data to InfluxDB

```bash
python push_to_influxdb.py --push-data
```

### Fetch Data from InfluxDB

```bash
python push_to_influxdb.py --fetch-data <start_date> <end_date>
```
Example:
```bash
python push_to_influxdb.py --fetch-data 2024-12-31T00:00:00 2024-12-31T23:59:59
```

## Notes

- The script expects the first column in each `.dat` file to be a timestamp (`YYYY-MM-DDTHH:MM:SS`), and the second column to be a float value.
- Only the first two columns are used; others are ignored.
- Data is written to the `energy_usage` measurement in