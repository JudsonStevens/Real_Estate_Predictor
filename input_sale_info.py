from bs4 import BeautifulSoup
import psycopg2
import requests
from configparser import ConfigParser
# import googlemaps
import geocoder
from dateutil import parser

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

def get_list_of_web_addresses():
    # Base URL and the URI used to obtain the HTML from the page.
    base_url = 'https://www.denvergov.org/apps/realproperty/'
    list_of_neighborhoods_URI = 'neighborhood.asp'

    # Go to the URL and grab the response using the requests library.
    response = requests.get(base_url + list_of_neighborhoods_URI)

    # Convert the response to a beautiful soup object using the html parser that we can then search.
    soup = BeautifulSoup(response.content, features='html.parser')

    # Initialize the array we're going to use to store the names of the neighborhoods and the link URI that allows us to navigate to the page.
    neighborhood_list = []

    # Once we have the beautiful soup object, we can grab all of the <a></a> tags, discard the ones that aren't neighborhoods, and save the name and web address into an array.
    for link in soup.find_all('a'):
        # We check to see if the first letter of the link is 'n'. If the first letter isn't 'n', we move on in the loop.
        if link['href'][0] != 'n':
            continue
        # Once we have the correct link, we can store the name of the neighborhood and the link text as a tuple into the array we initialized.
        else:
            neighborhood_list.append((link.contents[0], link['href']))

    # Use the database initialize method to start a connection to our database and return the connection along with the cursor.
    cur, conn = database_connect()

    # Use the cursor to execute the insert in order to save the neighborhood and link text. 
    # We use the %s operator in order to take advantage of the sanitization of the postgreSQL database. 
    # Not really necessary in this case, but a good habit to get into.
    for entry in neighborhood_list:
        try:
            cur.execute("""
                            INSERT INTO denver_sale_data_neighborhood_urls
                            (neighborhood_web_address, neighborhood_name)
                            VALUES
                            (%s, %s)
                        """,
                            (entry[1], entry[0])
                        )
            # Use the connection variable to commit the insertion every loop.
            conn.commit()
            # I like to have a visual list of the entries as they are saved.
            print(f'Saved the neighborhood {entry[0]}')
        # Catch any errors and print them out.
        except Exception as error:
            print(error)
    cur.close()
    conn.close()
    print('Database connection closed.')

def get_sale_info():
    # Connect to the database and grab all of the neighborhood URI's in order to reach each page.
    cur, conn = database_connect()
    cur.execute("""
                    SELECT neighborhood_web_address
                    FROM denver_sale_data_neighborhood_urls
                """)
    uris = cur.fetchall()
    base_url = 'https://www.denvergov.org/apps/realproperty/'
    uris = [item[0] for item in uris]
    # gmaps = googlemaps.Client(key=config('google_maps_api')['key'])
    # Length of uris is 170
    # 0-100 done so far
    
    results = []
    for entry in uris[170:171]:
        try:
            response = requests.get(base_url + entry)
            soup = BeautifulSoup(response.content, features='html.parser')
            # Iterate through every <tr> tag and grab the text out of it.
            for element in soup.find_all('tr')[3:]:
                list_data = element.text.replace(',', '').replace("\n", ",").replace("\xa0", ",").replace("\r", ",").replace("\t", ',').split(',')
                list_data = [x.split('-')[0] for x in list_data if x]
                if isinstance(int(list_data[0][0]), int):
                    geo_results = geocoder.osm(list_data[1] + ', Denver, CO').json
                    list_data.append(geo_results['lat'])
                    list_data.append(geo_results['lng'])
                    results.append(list_data)
                    print('Geocoding data...')
                else:
                    continue
        except Exception as error:
            print(error)
    conn.close()
    return results

def record_sale_info():
    cur, conn = database_connect()

    results = get_sale_info()

    for result in results:
        cur.execute("""
                        INSERT INTO denver_sale_data
                        (sale_price, address, sale_date, parcel_id, geographic_location)
                        VALUES
                        (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                    """,
                        (float(result[3].replace("$", "")), result[1], parser.parse(result[2]), result[0], result[4], result[5])
                    )
    conn.commit()
    conn.close()
    print("Closing database connection...")



if __name__ == '__main__':
    record_sale_info()
    