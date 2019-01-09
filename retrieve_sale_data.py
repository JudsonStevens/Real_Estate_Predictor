from bs4 import BeautifulSoup
import psycopg2
import requests
from configparser import ConfigParser
from datetime import date

def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')
    return db

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

if __name__ == '__main__':
    get_list_of_web_addresses()


