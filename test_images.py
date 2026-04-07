"""Quick test to verify image loading works."""
from data_loader import DataLoader

try:
    print("Loading data with images...")
    dl = DataLoader(sample_size=100)
    df = dl.get_dataframe()

    print(f"✓ Columns loaded: {list(df.columns)}")
    print(f"✓ Total rows: {len(df)}")

    if 'image' in df.columns:
        print(f"✓ Image column found")
        img_val = df['image'].iloc[0]
        print(f"✓ Sample image value: {repr(img_val)}")
        print(f"✓ Image type: {type(img_val)}")
        print(f"✓ Non-null images: {df['image'].notna().sum()}")

        # Show a few sample images
        print("\nFirst 3 images:")
        for i in range(min(3, len(df))):
            print(f"  [{i}]: {df['image'].iloc[i]}")
