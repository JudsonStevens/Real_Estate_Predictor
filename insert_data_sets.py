import psycopg2
import geocoder
import csv
from pyproj import Proj, transform
from datetime import datetime
from configparser import ConfigParser

def config(section='postgresql', filename='database.ini'):
    parser = ConfigParser()
    parser.read(filename)

    arguments = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            arguments[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')
    return arguments

def database_connect():
    conn = None
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        cur = conn.cursor()

        return cur, conn
    except Exception as error:
        print(error)


def main():
  curs, conn = database_connect()
  csv_file = './CSV_Files/liquor_licenses.csv'

  # ## Create the table needed.
  # sql = """
  #       CREATE TABLE liquor_license(
  #         id            INTEGER PRIMARY KEY,
  #         location      GEOMETRY(Point, 4326),
  #         full_address  VARCHAR(256),
  #         business_name VARCHAR(256),
  #         license_type  VARCHAR(256),
  #         end_date      DATE
  #       )
  #     """
  # curs.execute(sql)
  # conn.commit()

  with open(csv_file, mode='r') as csv_data_set:
    csv_reader = csv.DictReader(csv_data_set)
    inProj = Proj(init='epsg:3502', preserve_units=True)
    outProj = Proj(init='epsg:4326')
    for i in range(1):
      next(csv_reader)
    for row in csv_reader:
      # result = geocoder.osm(f'{row['FULL_ADDRESS']}' + ', Denver, CO')
      # lat = result.osm['x']
      # lon = result.osm['y']
      # records_list = records_list.append(tuple([lat, lon, row['FULL_ADDRESS'], row['BUS_PROF_NAME'], row['LICENSES'], row['end_date']]))
      longitudeUSFt, latitudeUSFt = row['X_COORD'], row['Y_COORD']
      longitude, latitude = transform(inProj, outProj, longitudeUSFt, latitudeUSFt)
      business_name, full_address, license_type, end_date = row['BUS_PROF_NAME'], row['FULL_ADDRESS'], row['LICENSES'], row['END_DATE']

      # Insert the values into the table
      print('Inserting values into the table....')
      curs.execute("INSERT INTO liquor_license (location, full_address, business_name, license_type, end_date) VALUES (ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s, %s, %s)", (longitude, latitude, full_address, business_name, license_type, datetime.strptime(end_date.split()[0], '%m/%d/%y').date()))
      conn.commit()
    conn.close()

if __name__ == "__main__":
  main()