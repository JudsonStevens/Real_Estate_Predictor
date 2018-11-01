import pyscopg2
import googlemaps

conn = pyscopg2.connect(host='localhost', database='postgis', user='postgres')
curs = conn.cursor
csv_file = 'liqour_licenses.csv'

## Create the table needed.
sql = """
        CREATE TABLE liquor_license(
          id            INTEGER PRIMARY KEY,
          location      GEOMETRY(Point, 4326),
          full_address  VARCHAR(256),
          business_name VARCHAR(256),
          license_type  VARCHAR(256),
          issue_date    TIMESTAMP
        )
      """

gmaps = googlemaps.Client(key='AIzaSyCN_MziHYEgvzN17SfhMIMeId3NCjKM7E8')

with open(csv_file, mode='r') as csv_data_set:
  csv_reader = csv.DictReader(csv_data_set)
  for i in range(1):
    next(csv_reader)
  for row in csv_reader:
    result = gmaps.geocode(f'{row['FULL_ADDRESS']}' + ', Denver, CO')
    lat = result[0]['geometry']['location']['lat']
    lon = result[0]['geometry']['location']['lng']
    records_list = []
    records_list = records_list.append(tuple([lat, lon, row['FULL_ADDRESS'], row['BUS_PROF_NAME'], row['LICENSES'], row['ISSUE_DATE']]))