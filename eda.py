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
train_df = train_df.astype(float)

# df_list = list(train_df)
# minPercentile = 0.15
# maxPercentile = 0.85
# for _ in range(8):
#     train_df[df_list[_]] = train_df[df_list[_]].clip((train_df[df_list[_]].quantile(minPercentile)),(train_df[df_list[_]].quantile(maxPercentile)))

def drop_outliers(df, field_name):
    distance = 1.5 * (np.percentile(df[field_name], 85) - np.percentile(df[field_name], 15))
    df.drop(df[df[field_name] > distance + np.percentile(df[field_name], 85)].index, inplace=True)
    df.drop(df[df[field_name] < np.percentile(df[field_name], 15) - distance].index, inplace=True)

columns = ['tax_assessment_amount', 'year_built', 'lot_size_sq_ft', 'living_area', 'bathrooms', 'total_rooms', 'last_sold_price', 'zestimate_amount']

for i in range(len(columns)):
  drop_outliers(train_df, columns[i])
  i += 1

print(train_df.dtypes)
print(train_df.head(5))
print(train_df.describe())



# print(train_df.zestimate_amount.unique())
# print(train_df.zestimate_amount.value_counts())
# constrains = train_df.select_dtypes(include=[np.number]).apply(lambda x: np.abs(stats.zscore(x)) < 3, reduce=False).all()
# train_df.drop(train_df.index[~constrains], inplace=True)
# train_df[(np.abs(stats.zscore(train_df)) < 3).all(axis=1)]?
# try:
# plt.figure(figsize=(6,4))
# sns.heatmap(train_df.corr(),cmap='Blues',annot=False) 

l = train_df.columns.values
number_of_columns=8
number_of_rows = len(l)-1/number_of_columns
plt.figure(figsize=(15,5*number_of_rows))
for i in range(0,len(l)):
    plt.subplot(number_of_rows + 1,number_of_columns,i+1)
    sns.set_style('whitegrid')
    sns.boxplot(train_df[l[i]],color='green',orient='v')
    plt.tight_layout()
# k = 8
# cols = train_df.corr().nlargest(k, 'zestimate_amount')['zestimate_amount'].index
# cm = train_df[cols].corr()
# plt.figure(figsize=(8,6))
# sns.heatmap(cm, annot=True, cmap='viridis')
# except ValueError:
#   pass
plt.figure(figsize=(12,12))
plt.scatter(train_df['zestimate_amount'], train_df['living_area'])
x_label = plt.ylabel('Lot Size in Sq Ft', fontsize=18, color='black')
y_label = plt.xlabel('Z Estimate Amount', fontsize=18, color='black')
# plt.axis([min(train_df['zestimate_amount']), max(train_df['zestimate_amount']), min(train_df['living_area']), max(train_df['living_area'])])
plt.tick_params(axis='x', colors='black')
plt.tick_params(axis='y', colors='black')
# plt.ticklabel_format(style='plain', axis='x')
# [i.set_color("white") for i in plt.gca().get_xticklabels()]
# [i.set_color("white") for i in plt.gca().get_yticklabels()]
plt.show()
#%%
