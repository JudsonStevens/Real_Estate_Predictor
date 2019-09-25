import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow import keras
from keras.layers import Dense
from keras import Sequential
from sklearn.ensemble import RandomForestRegressor
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import metrics
from scipy.stats import skew

def main():
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

  train_target = train_df.zestimate_amount
  train_predictors = train_df.drop('zestimate_amount', axis=1)

  predictor_train, predictor_test, target_train, target_test = train_test_split(train_predictors, train_target, test_size=0.3)

  # This will transform the target variable using the log function
  train_target = np.log1p(train_target)

  # This will transfer the skewed predictor variables. 
  skewed_feats = train_predictors.apply(lambda x: skew(x.dropna()))
  skewed_feats = skewed_feats[skewed_feats > .75]
  skewed_feats = skewed_feats.index

  train_predictors = np.log1p(train_predictors[skewed_feats])





  # print(x_train.shape, y_train.shape)
  # print(x_test.shape, y_test.shape)

  # my_model = RandomForestRegressor()
  # my_model.fit(x_train, y_train)

  # predicted_prices = my_model.predict(x_test)
  # score = my_model.score(x_test, y_test)

  # print(predicted_prices)
  # print(score)


if __name__ == "__main__":
  main()