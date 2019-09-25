#%%
import seaborn as sns
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
# Drop a row that happened to contain the text zestimate_amount for some reason
train_df = train_df[~train_df['zestimate_amount'].isin(['zestimate_amount'])]
# Turn all of the values to floats
train_df = train_df.astype(float)

def drop_outliers(df, field_name):
    distance = 1.5 * (np.percentile(df[field_name], 85) - np.percentile(df[field_name], 15))
    df.drop(df[df[field_name] > distance + np.percentile(df[field_name], 85)].index, inplace=True)
    df.drop(df[df[field_name] < np.percentile(df[field_name], 35) - distance].index, inplace=True)

columns = ['tax_assessment_amount', 'year_built', 'lot_size_sq_ft', 'living_area', 'bathrooms', 'total_rooms', 'last_sold_price', 'zestimate_amount']

for i in range(len(columns)):
  drop_outliers(train_df, columns[i])
  i += 1

print(train_df.dtypes)
print(train_df.head(5))
print(train_df.describe())

# Correlation heatmap of the data
plt.figure(figsize=(6,4))
sns.heatmap(train_df.corr(),cmap='Blues',annot=False) 

# Box plot of the data
l = train_df.columns.values
number_of_columns=8
number_of_rows = len(l)-1/number_of_columns
plt.figure(figsize=(15,5*number_of_rows))
for i in range(0,len(l)):
    plt.subplot(number_of_rows + 1,number_of_columns,i+1)
    sns.set_style('whitegrid')
    sns.boxplot(train_df[l[i]],color='green',orient='v')
    plt.tight_layout()

# Scatter plot of two pieces of the data
plt.figure(figsize=(18,18))
plt.scatter(train_df['zestimate_amount'], train_df['lot_size_sq_ft'])
x_label = plt.ylabel('Lot Size in Sq Ft', fontsize=18, color='black')
y_label = plt.xlabel('Z Estimate Amount', fontsize=18, color='black')
plt.tick_params(axis='x', colors='black')
plt.tick_params(axis='y', colors='black')
plt.show()

# Joint plot of two pieces of the data
sns.jointplot(x=train_df['living_area'], y=train_df['zestimate_amount'], kind='reg')

#%%