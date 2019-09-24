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
train_df = train_df[~train_df['zestimate_amount'].isin(['zestimate_amount'])]

print(train_df.head(5))
print(train_df.describe())
# print(train_df.zestimate_amount.unique())
# print(train_df.zestimate_amount.value_counts())

# try:
plt.figure(figsize=(6,4))
sns.heatmap(train_df.astype(float).corr(),cmap='Blues',annot=False) 
# k = 8
# cols = train_df.corr().nlargest(k, 'zestimate_amount')['zestimate_amount'].index
# cm = train_df[cols].corr()
# plt.figure(figsize=(8,6))
# sns.heatmap(cm, annot=True, cmap='viridis')
# except ValueError:
#   pass

#%%
