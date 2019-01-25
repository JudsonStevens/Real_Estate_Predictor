#%%
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
from scipy import stats

train_df = pd.read_csv('DenverHousingData.csv')
train_df = train_df.drop(['latitude', 'longitude', 'full_address', 'comparables_link', 'use_code',
                          'tax_assessment_year', 'last_sold_date', 'region_name', 'region_type', 
                          'zindex_value_of_region', 'zillow_id'], axis=1)
# Drop the rows that contain any NA's
train_df = train_df.dropna()
# Drop the rows that contain any values in any column equal to 0
train_df = train_df[(train_df != 0).all(1)]
# for column in train_df.columns.values.tolist():
#   train_df[f'{column}'].replace(0, train_df[f'{column}'].mean())
z = np.abs(stats.zscore(train_df))
train_df = train_df[(z < 3).all(axis=1)]
# train_df = train_df[np.abs(train_df.living_area - train_df.living_area.mean()) <= (3*train_df.living_area.std())]
# train_df = train_df[np.abs(train_df.last_sold_price - train_df.last_sold_price.mean()) <= (3*train_df.last_sold_price.std())]
# train_df = train_df[np.abs(train_df.year_built - train_df.year_built.mean()) <= (3*train_df.year_built.std())]
# train_df = train_df[np.abs(train_df.zestimate_amount - train_df.zestimate_amount.mean()) <= (3*train_df.zestimate_amount.std())]
# train_df = train_df[np.abs(train_df.lot_size_sq_ft - train_df.lot_size_sq_ft.mean()) <= (3*train_df.lot_size_sq_ft.std())]
# train_df = train_df[(np.abs(stats.zscore(train_df)) < 3).all(axis=1)]

## Issue with the lot size, it isn't dropping the largest values, probably because they pull the mean/std so high.

plt.figure(figsize=(12,12))
print((train_df['lot_size_sq_ft']).head(5))
print(max(train_df['lot_size_sq_ft']))
print((train_df['zestimate_amount']).head(5))
plt.scatter(train_df['zestimate_amount'], train_df['living_area'])
x_label = plt.ylabel('Lot Size in Sq Ft', fontsize=18, color='white')
y_label = plt.xlabel('Z Estimate Amount', fontsize=18, color='white')
# plt.axis([min(train_df['zestimate_amount']), max(train_df['zestimate_amount']), min(train_df['living_area']), max(train_df['living_area'])])
plt.tick_params(axis='x', colors='white')
plt.tick_params(axis='y', colors='white')
plt.ticklabel_format(style='plain')
# [i.set_color("white") for i in plt.gca().get_xticklabels()]
# [i.set_color("white") for i in plt.gca().get_yticklabels()]
plt.show()

# corr = train_df.corr()
# fig, ax = plt.subplots(figsize=(15, 15))
# ax.matshow(corr)
# plt.xticks(range(len(corr.columns)), corr.columns);
# plt.yticks(range(len(corr.columns)), corr.columns);
# plt.tick_params(axis='x', colors='white')
# plt.tick_params(axis='y', colors='white')

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