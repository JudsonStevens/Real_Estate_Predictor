import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow import keras
from keras.layers import Dense
from keras import Sequential

def main():
  train_df = pd.read_csv('DenverHousingData.csv', index_col='zillow_id')
  train_df = train_df.drop(['latitude', 'longitude', 'full_address', 'comparables_link', 'use_code',
                            'tax_assessment_year', 'tax_assessment_amount', 'last_sold_date', 'last_sold_price', 
                            'region_name', 'region_type', 'zindex_value_of_region'], axis=1)
  train_df = train_df.dropna()
  train_df = train_df[np.abs(train_df.living_area - train_df.living_area.mean()) <= (3*train_df.living_area.std())]
  train_df = train_df.dropna()
  # print(train_df.head(1))

  target = 'zestimate_amount'

  print(train_df.head(1))
  new_train = train_df.drop(target, axis=1)
  scaler = MinMaxScaler(feature_range=(0, 1))
  y_scaler = MinMaxScaler(feature_range=(0, 1))
  scaled_train_df = scaler.fit_transform(new_train)
  scaled_train_2 = y_scaler.fit_transform(train_df[[target]])

  # new = pd.DataFrame(scaled_train, columns = train_df.columns)
  # print(new.head(10))
  # print(f"Note: median values were scaled by multiplying by {scaler.scale_[5]} and adding {scaler.min_[5]}.")
  # multiplied_by = scaler.scale_[5]
  # added = scaler.min_[5]

  scaled_train_df = pd.DataFrame(scaled_train_df, columns = new_train.columns)
  scaled_train_2 = pd.DataFrame(scaled_train_2)

  y = scaled_train_2.values
  x = scaled_train_df.values
  model = Sequential()

  model.add(Dense(50, input_dim = 5, activation = 'relu'))
  model.add(Dense(70, activation = 'relu'))
  model.add(Dense(70, activation = 'relu'))
  model.add(Dense(50, activation = 'relu'))
  model.add(Dense(1, activation = 'sigmoid'))

  model.compile(loss='mean_squared_error', optimizer='adam')


  model.fit(x[100:, :], y[100:, :], epochs = 500, shuffle = True, verbose = 2)
  # y2 = y[:2]
  # y2 -= added
  # y2 /= multiplied_by
  # print(y2)
  # print(train_df[:2])
  prediction = model.predict(x[:1, :])
  print(y_scaler.inverse_transform(prediction)[0][0])
  import code; code.interact(local=dict(globals(), **locals()))
  # y_0 = prediction[0][0]
  # y_0 -= added
  # y_0 /= multiplied_by



if __name__ == "__main__":
  main()