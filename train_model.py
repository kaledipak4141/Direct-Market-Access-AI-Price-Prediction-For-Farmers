import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle

# Dataset load
data = pd.read_csv("data/crop_price_maharashtra.csv")

# convert categorical variables to numeric
data["crop"] = data["crop"].astype("category").cat.codes
data["district"] = data["district"].astype("category").cat.codes

X = data[["crop","district","month"]]
y = data["modal_price"]

# Model train
model = RandomForestRegressor()
model.fit(X,y)

# Save model
pickle.dump(model, open("model/model.pkl","wb"))

print("Model successfully trained")