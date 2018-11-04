#%%
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
from scipy import stats

train_df = pd.read_csv('DenverHousingData.csv')
train_df = train_df.drop(['latitude', 'longitude', 'full_address', 'comparables_link', 'use_code',
                          'tax_assessment_year', 'tax_assessment_amount', 'last_sold_date', 'region_name', 'region_type', 'zindex_value_of_region'], axis=1)
train_df = train_df.dropna() 

train_df = train_df[np.abs(train_df.living_area - train_df.living_area.mean()) <= (3*train_df.living_area.std())]
train_df = train_df[np.abs(train_df.last_sold_price - train_df.last_sold_price.mean()) <= (3*train_df.last_sold_price.std())]
train_df = train_df[np.abs(train_df.year_built - train_df.year_built.mean()) <= (3*train_df.year_built.std())]
# train_df = train_df[(np.abs(stats.zscore(train_df)) < 3).all(axis=1)]

plt.figure(figsize=(12,12))
plt.scatter(train_df['last_sold_price'], train_df['year_built'])
plt.ylabel('Year Built', fontsize=18)
plt.xlabel('Last Sold Price', fontsize=18)
plt.show()



# 'latitude': row["LATITUDE"], 
#                             'longitude': row["LONGITUDE"], 
#                             'full_address': row["FULL_ADDRESS"], 
#                             'zillow_id': z_id,
#                             'comparables_link': comp_link,
#                             'use_code': use_code,
#                             'tax_assessment_year': tax_as_year,
#                             'tax_assessment_amount': tax_as_amount,
#                             'year_built': year_built,
#                             'lot_size_sq_ft': lot_size,
#                             'living_area': living,
#                             'bathrooms': baths,
#                             'total_rooms': total_rooms,
#                             'last_sold_date': last_sold_date,
#                             'last_sold_price': last_sold_price,
#                             'zestimate_amount': z_amount,
#                             'region_name': reg_name,
#                             'region_type': reg_type,
#                             'zindex_value_of_region': z_value_reg

  # 'latitude', 'longitude', 'full_address', 'comparables_link', 'use_code',
  #                           'tax_assessment_year', 'tax_assessment_amount', 'last_sold_date', 'last_sold_price', 
  #                           'region_name', 'region_type', 'zindex_value_of_region'