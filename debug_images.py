"""Debug image loading."""
from data_loader import DataLoader
import pandas as pd

dl = DataLoader(sample_size=5)
df = dl.get_dataframe()

print("Total rows:", len(df))
print("Columns in dataframe:", list(df.columns))
print("Image column exists:", 'image' in df.columns)

if 'image' in df.columns:
    print("\nFirst 5 image values:")
    for i in range(min(5, len(df))):
        img = df['image'].iloc[i]
        print(
            f"Row {i}: {type(img)} | Length: {len(str(img))} | Value: {str(img)[:100]}")
else:
    print("ERROR: Image column not found!")
    print("Available columns:", df.columns.tolist())
