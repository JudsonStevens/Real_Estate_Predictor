import psycopg2
import geocoder
import csv
from pyproj import Proj, transform
from datetime import datetime
from configparser import ConfigParser
import googlemaps

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


def input_liquor_store_data():
  cur, conn = database_connect()
  csv_file = './CSV_Files/liquor_licenses.csv'

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
      cur.execute("""INSERT INTO liquor_license (location, full_address, business_name, license_type, end_date) 
                    VALUES (ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s, %s, %s)""", 
                     (longitude, latitude, full_address, business_name, license_type, datetime.strptime(end_date.split()[0], '%m/%d/%y').date()))
      conn.commit()
    conn.close()

def input_dog_park_data():
  cur, conn = database_connect()
  csv_file = './CSV_Files/dog_parks.csv'

  gmaps = googlemaps.Client(key=config('google_maps_api')['key'])
  with open(csv_file, mode='r') as csv_data_set:
    csv_reader = csv.DictReader(csv_data_set)
    for i in range(1):
      next(csv_reader)
    for row in csv_reader:
      place_id = gmaps.find_place(f"{row['LOCATION']}, Denver CO", "textquery")
      place = gmaps.place(place_id['candidates'][0]['place_id'])
      latitude, longitude = place['result']['geometry']['location']['lat'], place['result']['geometry']['location']['lng']
      if row['WATER'] == 'None':
        water_available = 'no'
      else:
        water_available = row['WATER']
      if row['SHADE'] == 'None':
        shaded = 'no'
      else:
        shaded = row['SHADE']
      park_name, fenced, number_of_acres = row['LOCATION'], row['FENCED'], float(row['GIS_ACRES'])
      
      print('Inserting values into the table....')
      cur.execute("""INSERT INTO dog_park (park_name, fenced, shaded, water_available, number_of_acres, location )
                    VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                    """,
                    (park_name, fenced, shaded, water_available, number_of_acres, longitude, latitude))
      conn.commit()
    conn.close()

def input_park_data():
  cur, conn = database_connect()
  csv_file = './CSV_Files-parks.csv'

  with open(csv_file, mode='r') as csv_data_set:
    csv_reader = csv.DictReader(csv_data_set)
    for i in rane(1):
      next(csv_reader)
    for row in csv_reader:
      print('Inserting values into the table....')
      cur.execute("""
                    INSERT INTO park (park_name, park_type, number_of_acres, year_park_started, location, park_image_URI, park_facilities)
                    VALUES
                    (%s, %s, %s, %s, ST_SetSRID(ST_MAKEPOINT(%s, %s), 4326), %s, %s)
                  """,
                  (row['FORMAL_NAME'], row['PARK_TYPE'], float(row['GIS_ACRES']), float(row['FIRST_AQ_DATE']), row['LONGITUTDE'], row['LATITUDE'], row['PHOTO'], row['FACILITIES']))
      conn.commit()
    conn.close()

if __name__ == "__main__":
  input_park_data()