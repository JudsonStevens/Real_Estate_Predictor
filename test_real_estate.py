import csv
import requests
from bs4 import BeautifulSoup

def main():
  api_key = "X1-ZWz18aonipipzf_a1050"
  prefix_url = "http://www.zillow.com/webservice/"
  city = "Denver"
  state = "CO"
  line_count = 0
  error_count = 0
  row_count = 0
  error_seven_count = 0

  with open('DenverAdresses.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for i in range((865+629+1)):
      next(csv_reader)
      line_count = 1
    with open('DenverHousingData.csv', mode='a', newline='') as write_file:
      headers = ['latitude', 'longitude', 'full_address', 'zillow_id', 'comparables_link', 'use_code', 'tax_assessment_year', 
                 'tax_assessment_amount', 'year_built', 'lot_size_sq_ft', 'living_area', 'bathrooms', 'total_rooms', 
                 'last_sold_date', 'last_sold_price', 'zestimate_amount', 'region_name', 'region_type', 'zindex_value_of_region']
      writer = csv.DictWriter(write_file, fieldnames=headers)
      for row in csv_reader:
        if error_count > 250 or line_count >= 900 or error_seven_count > 150:
          print(f'The error count is {error_count}.')
          print(f'The row count is {row_count}.')
          break
        if line_count == 0:
          print('Starting loop.')
          writer.writeheader()
          line_count += 1
          row_count += 1
        if row["UNIT_TYPE"] == 'None':
          address = row["FULL_ADDRESS"].strip().replace(" ", "+")
          url = prefix_url + "GetDeepSearchResults.htm?zws-id=" + api_key + "&address=" + address + "&citystatezip=" + city + "%2C+" + state
          response = requests.get(url)
          soup = BeautifulSoup(response.content, 'xml')
          if soup.code.text == '7':
            print(f'API request refused.')
            error_seven_count += 1 
            continue
          if soup.code.text == '3' or soup.code.text == '4':
            print(f'Encountered code {soup.code.text}, ending program.')
            break
          if soup.code.text == '508':
            print(f'Address could not be found.')
            continue
          if soup.code.text != '0':
            print(f'Encountered code {soup.code.text}.')
            error_count += 1
            row_count += 1
            continue
          try:
            z_id = 0 if soup.zpid is None else soup.zpid.text
            comp_link = '' if soup.comparables is None else soup.comparables.text
            use_code = '' if soup.useCode is None else soup.useCode.text
            tax_as_year = 0 if soup.taxAssessmentYear is None else soup.taxAssessmentYear.text
            tax_as_amount = 0 if soup.taxAssessment is None else soup.taxAssessment.text
            year_built = 0 if soup.yearBuilt is None else soup.yearBuilt.text
            lot_size = 0 if soup.lotSizeSqFt is None else soup.lotSizeSqFt.text
            living = 0 if soup.finishedSqFt is None else soup.finishedSqFt.text
            baths = 0 if soup.bathrooms is None else soup.bathrooms.text
            total_rooms = 0 if soup.totalRooms is None else soup.totalRooms.text
            last_sold_date = 0 if soup.lastSoldDate is None else soup.lastSoldDate.text
            last_sold_price = 0 if soup.lastSoldPrice is None else soup.lastSoldPrice.text
            z_amount = 0 if soup.zestimate.amount is None else soup.zestimate.amount.text
            reg_name = '' if soup.localRealEstate.region is None else soup.localRealEstate.region['name']
            reg_type = '' if soup.localRealEstate.region is None else soup.localRealEstate.region['type']
            if soup.localRealEstate.region is None or soup.localRealEstate.region.zindexValue is None:
              z_value_reg = 0 
            else:
              z_value_reg = soup.localRealEstate.region.zindexValue.text
          except AttributeError as error:
            print(f'Error {error}')
            continue
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
  # resp = requests.get(url)

  # with open('text.xml', 'wb') as f:
  #   f.write(resp.content)
  # soup = BeautifulSoup(resp.content, 'xml')
  # tag = soup.bedrooms
  # print(tag.text)

if __name__ == "__main__":
  main()

### Pull in one address and run it using deep search results. Extract the information and write it to a CSV. 950 per day, exclude apartments, only houses. Store lat/long in order to eventually
### plot on Google maps or Mapbox. Make sure to include sleeps in the loop in order to accomodate network deficiencies. Account for zillow codes in order to stop if no longer working. Error
### count? 