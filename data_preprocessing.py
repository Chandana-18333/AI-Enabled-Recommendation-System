import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv("dataset.csv")

# Display first 5 rows
print("First 5 rows:")
print(df.head())

# Check missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Drop missing values
df = df.dropna()

print("\nAfter removing missing values:")
print(df.isnull().sum())

# Save cleaned dataset
df.to_csv("cleaned_dataset.csv", index=False)

print("\nData preprocessing completed successfully!")