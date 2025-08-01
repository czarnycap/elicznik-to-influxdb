import os
import json
from influxdb import InfluxDBClient
import csv
from datetime import datetime, timedelta
import argparse
from dotenv import load_dotenv  

# Load environment variables from a .env file
load_dotenv()

# Read environment variables
INFLUXDB_HOST = os.getenv('INFLUXDB_HOST', 'localhost')
INFLUXDB_PORT = int(os.getenv('INFLUXDB_PORT', 1234))
INFLUXDB_DATABASE = os.getenv('INFLUXDB_DATABASE', 'db')
INFLUXDB_USER = os.getenv('INFLUXDB_USER', 'user')
INFLUXDB_PASSWORD = os.getenv('INFLUXDB_PASSWORD', 'pssword')
INPUT_FOLDER = os.getenv('INPUT_FOLDER', './')



def read_files_from_input_folder():
    """
    Reads .dat files from the input folder, parses each file, and yields data points.
    This function iterates over all files in the specified input folder. For each file
    that ends with the .dat extension, it opens the file and reads its contents using
    a CSV reader. Each row in the file is expected to have at least two columns. The
    first column is parsed as a timestamp, and the second column is used as the value
    for the data point. The function yields each data point as a dictionary with the
    following structure:
    {
        "time": <timestamp>,
            "value": <value>
    Yields:
        dict: A dictionary representing a data point with a timestamp and value.
    """
    for filename in os.listdir(INPUT_FOLDER):

        if filename.endswith(".dat"):
            file_path = os.path.join(INPUT_FOLDER, filename)
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) < 2:
                        continue
                    timestamp = row[0]
                    try:
                        timestamp = datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%S')
                        value = float(row[1])
                    except Exception as e:
                        print(f"Skipping row due to error: {e}")
                        continue

                    data_point = {
                        "measurement": "energy_usage",
                        "time": timestamp.isoformat(),
                        "fields": {
                            "value": value
                        }
                    }
                    yield data_point

def store_data_in_influxdb(data_point):
        client = InfluxDBClient(
            host=INFLUXDB_HOST,
            port=INFLUXDB_PORT,
            username=INFLUXDB_USER,
            password=INFLUXDB_PASSWORD,
            database=INFLUXDB_DATABASE
        )
        try:
            client.write_points([data_point])
            print(f"Data point {data_point} written to InfluxDB successfully.")
        except Exception as e:
            print(f"Failed to write data point to InfluxDB: {e}")
        finally:
            client.close()



def test_influxdb_connection():
    try:
        client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, username=INFLUXDB_USER, password=INFLUXDB_PASSWORD)
        client.ping()
        print("Connected to InfluxDB successfully.")
    except Exception as e:
        print(f"Failed to connect to InfluxDB: {e}")

def fetch_data_from_influxdb(start_date, end_date):
    """
    Fetches data from InfluxDB between start_date and end_date.
    Accepts dates in 'YYYY-MM-DD' format and converts them to RFC3339.
    """
    # If only date is provided, convert to full RFC3339 timestamps
    try:
        if len(start_date) == 10 and len(end_date) == 10:
            # Parse as date, add time and Z
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            start_date = start_dt.strftime('%Y-%m-%dT00:00:00Z')
            end_date = end_dt.strftime('%Y-%m-%dT23:59:59Z')
        elif len(start_date) == 19 and len(end_date) == 19:
            # If time is provided but no Z, add Z
            if not start_date.endswith('Z'):
                start_date += 'Z'
            if not end_date.endswith('Z'):
                end_date += 'Z'
    except Exception as e:
        print(f"Invalid date format: {e}")
        return

    client = InfluxDBClient(
        host=INFLUXDB_HOST,
        port=INFLUXDB_PORT,
        username=INFLUXDB_USER,
        password=INFLUXDB_PASSWORD,
        database=INFLUXDB_DATABASE
    )
    query = f"SELECT * FROM energy_usage WHERE time >= '{start_date}' AND time <= '{end_date}'"
    try:
        result = client.query(query)
        points = list(result.get_points())
        for point in points:
            print(point)
    except Exception as e:
        print(f"Failed to fetch data from InfluxDB: {e}")
    finally:
        client.close()

# Directory containing the output files
OUTPUT_DIR = '/home/czarnycap/5tb/repos/elicznik/output'

def main():
    """
    Main function to handle command-line arguments and execute corresponding actions.

    This function uses argparse to parse command-line arguments and performs actions
    based on the provided arguments. It supports the following options:
    
    --test-connection : Tests the connection to InfluxDB.
    --push-data       : Pushes data from files to InfluxDB.

    Usage:
        python push_to_influxdb.py --test-connection
        python push_to_influxdb.py --push-data

    Args:
        --test-connection (bool): If specified, tests the connection to InfluxDB.
        --push-data (bool): If specified, pushes data from files to InfluxDB.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description='Push data to InfluxDB.')
    parser.add_argument('--test-connection', action='store_true', help='Test connection to InfluxDB')
    parser.add_argument('--push-data', action='store_true', help='Push data from files to InfluxDB')
    parser.add_argument('--fetch-data', nargs=2, metavar=('start_date', 'end_date'), help='Fetch data from InfluxDB between start_date and end_date')
    args = parser.parse_args()

    if args.test_connection:
        test_influxdb_connection()

    if args.fetch_data:
        start_date, end_date = args.fetch_data
        fetch_data_from_influxdb(start_date, end_date)

    if args.push_data:
        for data_point in read_files_from_input_folder():
            print(data_point)
            store_data_in_influxdb(data_point)

if __name__ == '__main__':
    main()
