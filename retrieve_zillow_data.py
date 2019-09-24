import csv
import requests
from bs4 import BeautifulSoup
from configparser import ConfigParser

def config(section='zillow_api_keys', filename='database.ini'):
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

def main():
  ## Set all of the variables needed for the rest of the function.
  api_keys = config()
  prefix_url = "http://www.zillow.com/webservice/"
  city = "Denver"
  state = "CO"
  line_count = 0
  error_count = 0
  row_count = 0
  error_seven_count = 0
  total_row_count = 0

  ## Open the main CSV with the addresses, initialize a dictionary reader with that CSV.
  with open('DenverAdresses.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    ## Skip to the current line. This is a sum of all of the row counts from running the program. Initialize the line count to 1 so it doesn't re-read the headers.
    # 865+629+1025+1743+1687+1901+1950+1934+1810+1516+275+1292+1288+1320+1323+1207+1197+1163+1544+1974+1000+1513+1+1250+1400+2262
    for i in range((865+629+1025+1743+1687+1901+1950+14348+1934+1810+1516+275+1292+1288+1320+1323+1207+1197+1163+1544+13873+1974+1000+1513+1+1250+1400+2262+1954+8749+8737+4000+15858)):
      next(csv_reader)
      line_count = 1
    
    ## Open up the CSV we'll be writing to and add a new line. Set the headers for the first run through.
    with open('DenverHousingData.csv', mode='a', newline='') as write_file:
      headers = ['latitude', 'longitude', 'full_address', 'zillow_id', 'comparables_link', 'use_code', 'tax_assessment_year', 
                 'tax_assessment_amount', 'year_built', 'lot_size_sq_ft', 'living_area', 'bathrooms', 'total_rooms', 
                 'last_sold_date', 'last_sold_price', 'zestimate_amount', 'region_name', 'region_type', 'zindex_value_of_region']
      writer = csv.DictWriter(write_file, fieldnames=headers)

      ## Start reading the address CSV.
      for api_key in api_keys.values():
        line_count = 0
        error_count = 0
        error_seven_count = 0
        for row in csv_reader:

          ## If the error count, the line count, or the code 7 error count are too high, print the error and row count and exit the program.
          if error_count > 250 or line_count >= 1000 or error_seven_count > 150:
            total_row_count += row_count
            print(f'The error count is {error_count}.')
            print(f'The row count is {row_count}.')
            print(f'The total row count is {total_row_count}')
            break

          ## If it's the first line, write the headers.
          if line_count == 0:
            print('Starting loop.')
            writer.writeheader()
            line_count += 1
            row_count += 1

          ## Make sure the entry is a house by ensuring the unit type is none. This excludes apartments and other housing types.
          if row["UNIT_TYPE"] == 'None':

            ## Grab the full address by stripping whitespaces and adding plus signs to serialize it to be used in the URL.
            address = row["FULL_ADDRESS"].strip().replace(" ", "+")

            ## Build the URL.
            url1 = prefix_url + "GetDeepSearchResults.htm?zws-id=" + api_key.strip('\"') + "&address=" + address + "&citystatezip=" + city + "%2C+" + state
              
            ## Use requests to get the response to the URL.
            response1 = requests.get(url1)

            ## store the URL response after beautiful soup parses the XML.
            soup1 = BeautifulSoup(response1.content, 'xml')

            ## Get the second url and information.
            # url2 = prefix_url + "GetUpdatedPropertyDetails.htm?zws-id=" + api_key.strip('\"') + "&zpid=" + soup1.zpid.text

            # response2 = requests.get(url2)

            # soup2 = BeautifulSoup(response2.content, 'xml')

            ## These are for the various response codes. Too many API requests consists of 3, 4, or 7. Not found address is 508. A response code of 0 means proceed.
            if soup1.code.text == '7' :
              print(f'API request refused.')
              row_count += 1
              error_seven_count += 1 
              continue
            if soup1.code.text == '3' or soup1.code.text == '4'  :
              print(f'Encountered code message {soup1.code.text}, ending program.')
              break
            if soup1.code.text == '508' :
              print(f'Address could not be found.')
              row_count += 1
              continue
            if soup1.code.text != '0' :
              print(f'Encountered code {soup1.code.text}.')
              error_count += 1
              row_count += 1
              continue

            ## Try to proceed with the following code. This code standardizes the error if one of the attributes is missing.
            try:
              z_id = soup1.zpid.text
              comp_link = soup1.comparables.text
              use_code = soup1.useCode.text
              tax_as_year = soup1.taxAssessmentYear.text
              tax_as_amount = soup1.taxAssessment.text
              year_built = soup1.yearBuilt.text
              lot_size = soup1.lotSizeSqFt.text
              living = soup1.finishedSqFt.text
              baths = soup1.bathrooms.text
              total_rooms = soup1.totalRooms.text
              last_sold_date = soup1.lastSoldDate.text
              last_sold_price = soup1.lastSoldPrice.text
              z_amount = soup1.zestimate.amount.text
              reg_name = soup1.localRealEstate.region['name']
              reg_type = soup1.localRealEstate.region['type']
              if soup1.localRealEstate.region is None or soup1.localRealEstate.region.zindexValue is None:
                z_value_reg = 0
              else:
                z_value_reg = soup1.localRealEstate.region.zindexValue
            except AttributeError as error:
              row_count += 1
              print(f'Error {error}')
              continue
            except TypeError as error:
              row_count += 1
              print(f'Error {error}')
              continue

            ## Try to write the data to the CSV.
            try:
              writer.writerow({'latitude': row["LATITUDE"], 
                              'longitude': row["LONGITUDE"], 
                              'full_address': row["FULL_ADDRESS"], 
                              'zillow_id': z_id,
                              'comparables_link': comp_link,
                              'use_code': use_code,
                              'tax_assessment_year': tax_as_year,
                              'tax_assessment_amount': tax_as_amount,
                              'year_built': year_built,
                              'lot_size_sq_ft': lot_size,
                              'living_area': living,
                              'bathrooms': baths,
                              'total_rooms': total_rooms,
                              'last_sold_date': last_sold_date,
                              'last_sold_price': last_sold_price,
                              'zestimate_amount': z_amount,
                              'region_name': reg_name,
                              'region_type': reg_type,
                              'zindex_value_of_region': z_value_reg
                              }) 
              print(f'Processed {row["FULL_ADDRESS"]}. This is line {line_count}.')
              line_count += 1
              row_count += 1
            except AttributeError as error:
              print(f'Request came back with missing value. Skipping {row["FULL_ADDRESS"]}.')
              continue
            except TypeError as error2:
              print(f'Request came back with missing value. Skipping {row["FULL_ADDRESS"]}.')
              continue
          else:
            continue

if __name__ == "__main__":
  main()

### Pull in one address and run it using deep search results. Extract the information and write it to a CSV. 950 per day, exclude apartments, only houses. Store lat/long in order to eventually
### plot on Google maps or Mapbox. Make sure to include sleeps in the loop in order to accomodate network deficiencies (not needed). Account for zillow codes in order to stop if no longer working. Error
### count? 



#Example updated property returned value
# <?xml version="1.0" encoding="utf-8"?>
# <UpdatedPropertyDetails:updatedPropertyDetails xmlns:UpdatedPropertyDetails="http://www.zillow.com/static/xsd/UpdatedPropertyDetails.xsd" 
#   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.zillow.com/static/xsd/UpdatedPropertyDetails.xsd http://www.zillowstatic.com/vstatic/80d5e73/static/xsd/UpdatedPropertyDetails.xsd">
#   <request>
#     <zpid>68051419</zpid>
#   </request>
#   <message>
#     <text>Request successfully processed</text>
#     <code>0</code>
#   </message>
#   <response>
#     <zpid>68051419</zpid>
#     <pageViewCount>
#       <currentMonth>1</currentMonth>
#       <total>1</total>
#     </pageViewCount>
#     <address>
#       <street>176 Hazel Ct</street>
#       <zipcode>80219</zipcode>
#       <city>Denver</city>
#       <state>CO</state>
#       <latitude>39.719609</latitude>
#       <longitude>-105.027215</longitude>
#     </address>
#     <links>
#       <homeDetails>http://www.zillow.com/homedetails/176-Hazel-Ct-Denver-CO-80219/68051419_zpid/</homeDetails>
#       <photoGallery>http://www.zillow.com/homedetails/176-Hazel-Ct-Denver-CO-80219/68051419_zpid/image=lightbox%3Dtrue</photoGallery>
#       <homeInfo>http://www.zillow.com/homedetails/176-Hazel-Ct-Denver-CO-80219/68051419_zpid/</homeInfo>
#     </links>
#     <images>
#       <count>4</count>
#       <image>
#         <url>https://photos.zillowstatic.com/p_d/ISxfuqybvck90j.jpg</url>
#         <url>https://photos.zillowstatic.com/p_d/IS10q5mkevwmopv.jpg</url>
#         <url>https://photos.zillowstatic.com/p_d/IS10qovvrwoi8bn.jpg</url>
#         <url>https://photos.zillowstatic.com/p_d/ISxc04ml6d1nkz.jpg</url>
#       </image>
#     </images>
#     <editedFacts>
#       <useCode>SingleFamily</useCode>
#       <bedrooms>4</bedrooms>
#       <bathrooms>3.0</bathrooms>
#       <finishedSqFt>2000</finishedSqFt>
#       <lotSizeSqFt>3125</lotSizeSqFt>
#       <yearBuilt>2004</yearBuilt>
#       <yearUpdated>2004</yearUpdated>
#       <numFloors>1</numFloors>
#       <numRooms>9</numRooms>
#       <basement>Finished</basement>
#       <roof>Shake / Shingle</roof>
#       <exteriorMaterial>Wood</exteriorMaterial>
#       <view>Mountain, City, Park</view>
#       <parkingType>Off-street, On-street</parkingType>
#       <heatingSources>Gas</heatingSources>
#       <heatingSystem>Forced air</heatingSystem>
#       <appliances>Dishwasher, Dryer, Freezer, Microwave, Range / Oven, Refrigerator, Washer</appliances>
#       <floorCovering>Carpet, Linoleum / Vinyl, Tile</floorCovering>
#       <rooms>Dining room, Family room, Laundry room, Master bath, Pantry, Recreation room, Walk-in closet</rooms>
#       <architecture>Other</architecture>
#     </editedFacts>
#   </response>
# </UpdatedPropertyDetails:updatedPropertyDetails><!-- H:001  T:49ms  S:1005  R:Tue Jun 25 18:58:40 PDT 2019  B:5.0.60981.2-hotfix_2019-06-25.cf7d3b9~hotfix-platform-for-2019-06-25.457adbe -->
