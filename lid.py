import pandas as pd
dataset_directory = "./LinkedIn_Dataset.pcl" #Change this according to your directory
dataset = pd.read_pickle(dataset_directory)

# Display DataFrame info
print("\nDataFrame Info:")
print(dataset.info())

# Display all column names
print("\nAll columns:")
print(dataset.columns.tolist())

# Display a single row in more detail
print("\nDetailed view of first row:")
print(dataset.iloc[0].to_dict())