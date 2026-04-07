<!-- <<<<<<< HEAD
# KHOJO-
Khojo is a fashion recommender system built with Streamlit and scikit-learn, using TF-IDF and cosine similarity to suggest similar products.  It features filters for price, rating, and discount, along with a favorites option. The app provides fast, real-time recommendations with a clean and user-friendly interface.
=======
# Khojo: Professional Fashion Recommender System

## Overview

**Khojo** is a modern web application for discovering similar fashion products using advanced machine learning. Built with Streamlit, it uses TF-IDF vectorization and cosine similarity to provide accurate product recommendations.

## 📂 Dataset

The dataset used in this project is too large to upload on GitHub.

You can download it from Google Drive:

🔗 https://drive.google.com/file/d/1MNJYgDZQZxc2O-KZqdoBSdwD0hw9nkKZ/view?usp=drive_link

After downloading, place it in the project folder:
### Version: 2.0
**Last Updated:** 2024

---

## Key Features

### Smart Recommendations
- **TF-IDF Powered**: Uses text-based vectorization for intelligent product matching
- **Cosine Similarity**: Calculates similarity between products for accurate recommendations
- **Top 10 Results**: Returns the 10 most similar products

### Advanced Filtering
- **Price Range Filter**: Find products within your budget
- **Rating Filter**: Show only highly-rated products (2.5+)
- **Discount Filter**: Filter by minimum discount percentage

### Favorites Management
- **Save Products**: Add favorite products to your personal collection
- **View Favorites**: Easy access to saved items
- **Quick Remove**: Remove items with a single click

### Data Insights
- **Dataset Overview**: View total products, price ranges, and average ratings
- **Interactive Stats**: Expandable statistics section
- **Real-time Filtering**: Results update instantly based on your criteria

### Professional UI
- **Modern Design**: Clean, responsive interface
- **Product Cards**: Beautifully formatted product information
- **Intuitive Layout**: Easy-to-use sidebar filters
- **Custom Styling**: Professional CSS with hover effects

---

## Project Structure

```
recommender-system/
├── app.py                    # Main Streamlit application
├── data_loader.py           # Data loading and preprocessing
├── recommender.py           # Recommendation engine logic
├── ui_components.py         # UI components and styling
├── favorites_manager.py      # Favorites/preferences management
├── myntra.csv               # Fashion product dataset
├── clothing.py              # Legacy testing file (optional)
└── README.md                # This file
```

---

## Technical Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **ML/NLP** | scikit-learn (TF-IDF, Cosine Similarity) |
| **Data Processing** | Pandas, NumPy |
| **Caching** | Streamlit @cache_resource |
| **State Management** | Streamlit Session State |

---

## Getting Started

### Prerequisites
```bash
Python 3.8+
```

### Installation

1. **Install Required Packages**
   ```bash
   pip install streamlit pandas scikit-learn
   ```

2. **Navigate to Project Directory**
   ```bash
   cd "recommender system"
   ```

3. **Run the Application**
   ```bash
   streamlit run app.py
   ```

4. **Access the App**
   - Open your browser to: `http://localhost:8501`

---

## How to Use

### Basic Search
1. Type a product name in the search box (e.g., "T-shirt", "Jeans", "Shoes")
2. Click "🔍 Get Recommendations"
3. Browse similar products

### Apply Filters
1. Adjust filters in the left sidebar:
   - **Price Range**: Set minimum and maximum price
   - **Minimum Rating**: Filter by star ratings
   - **Minimum Discount**: Show discounted items
2. Results update automatically

### Manage Favorites
1. Click the **heart** button to add a product to favorites
2. Click **View Favorites** in sidebar to see all saved items
3. Click **X** next to a favorite to remove it
4. Click **Clear All Favorites** to remove everything

---

## Module Documentation

### `data_loader.py`
**Purpose**: Manages data loading and preprocessing

**Key Classes**:
- `DataLoader`: Handles CSV loading, data cleaning, and feature engineering

**Methods**:
- `load_and_process()`: Cleans and prepares data
- `get_dataframe()`: Returns processed DataFrame
- `get_stats()`: Returns dataset statistics

### `recommender.py`
**Purpose**: Implements the recommendation engine

**Key Classes**:
- `RecommendationEngine`: Handles TF-IDF and similarity calculations

**Methods**:
- `recommend(product_name, top_n=10)`: Get top N recommendations
- `filter_by_price()`: Filter by price range
- `filter_by_rating()`: Filter by minimum rating
- `filter_by_discount()`: Filter by minimum discount

### `ui_components.py`
**Purpose**: Provides reusable UI components and styling

**Key Functions**:
- `apply_custom_styling()`: Apply custom CSS
- `display_product_card()`: Display individual product
- `display_stats_boxes()`: Display statistics
- `get_sidebar_filters()`: Get filter values from sidebar
- `display_no_results()`: Show "no results" message

### `favorites_manager.py`
**Purpose**: Manages user favorites using Streamlit session state

**Key Methods**:
- `add_favorite()`: Add product to favorites
- `remove_favorite()`: Remove product from favorites
- `get_favorites()`: Get all favorites
- `is_favorite()`: Check if product is favorited
- `clear_favorites()`: Clear all favorites

### `app.py`
**Purpose**: Main Streamlit application

**Features**:
- Page configuration and styling
- Data loading and caching
- Search interface
- Recommendations display
- Favorites management

---

## 🎨 UI Enhancements

### Styling Features
- **Custom CSS**: Professional gradient backgrounds
- **Product Cards**: Hover effects and smooth transitions
- **Badges**: Color-coded price, rating, and discount badges
- **Responsive Layout**: Works on desktop and tablet
- **Icons**: Visual indicators

### User Experience
- **Loading State**: Spinner while fetching recommendations
- **Toast Notifications**: Feedback when adding/removing favorites
- **Empty States**: Helpful messages when no results found
- **Expandable Sections**: Dataset stats in collapsible section
- **Clear Call-to-Action**: Prominent search and filter buttons

---

## How It Works

### Algorithm Overview
1. **TF-IDF Vectorization**: Converts product names and sellers into numerical vectors
2. **Cosine Similarity**: Calculates similarity between product vectors
3. **Ranking**: Products ranked by similarity score and rating
4. **Filtering**: Applied after recommendations for refined results

### Data Flow
```
User Input 
    ↓
Search & Match Product 
    ↓
Calculate Similarity Scores 
    ↓
Sort & Filter Results 
    ↓
Display Formatted Cards 
    ↓
Save to Favorites (Optional)
```

---

## Performance Features

- **Caching**: Data and recommender engine cached for instant responses
- **Efficient Vectorization**: Pre-computed TF-IDF matrix
- **Optimized Filtering**: Pandas-based filtering for speed
- **Session State**: Favorites stored in memory

---

## Error Handling

- **File Not Found**: Clear error message if CSV is missing
- **Data Validation**: Automatic cleanup of invalid/missing data
- **Invalid Input**: Graceful handling of empty searches
- **Type Conversion**: Robust numeric conversion with error handling

---

## Future Enhancements

- [ ] Product images display
- [ ] User activity tracking
- [ ] Personalized recommendations based on history
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Advanced filters (size, color, brand)
- [ ] Product comparison tool
- [ ] Export favorites as CSV/PDF

---

## Notes

- Dataset: Uses 10,000 sampled products for performance
- CSV Format: Requires columns: `name`, `price`, `rating`, `seller`, `discount`
- Python Version: Compatible with Python 3.8+

---

## Contributing

To add new features:
1. Create new modules following existing patterns
2. Add docstrings to all functions
3. Update this README with new features
4. Test thoroughly before committing

---

## License

This project is open source. Feel free to use and modify as needed.

---

## Tips & Tricks

- **Quick Search**: Start with broad categories (e.g., "shirt" vs specific model)
- **Filter Optimization**: Start broad, then narrow with filters
- **Favorites Strategy**: Use favorites to create a wishlist
- **Price Research**: Use price filter to find budget alternatives

---

## Troubleshooting

### App won't start
- Ensure all packages are installed: `pip install -r requirements.txt`
- Check that `myntra.csv` is in the same directory

### Slow recommendations
- Reduce `sample_size` in `data_loader.py`
- Clear Streamlit cache: `streamlit cache clear`

### Favorites not saving
- Ensure you're clicking the heart button fully
- Check browser console for errors

---

**Built with ❤️ using Streamlit**
>>>>>>> 6a689bc (initial commit)
#   K h o j o - R e c o m m e n d 
 
  -->

# 🛍️ Khojo – Product Recommendation System

## 📌 Overview

Khojo is a machine learning-based product recommendation system designed to suggest relevant fashion items to users based on their preferences. The system analyzes product features and user behavior to provide personalized recommendations.

---

## 🚀 Features

* 🔍 Content-based recommendation system
* 📊 Data preprocessing and feature engineering
* 🤖 Machine Learning model for similarity matching
* 📈 Efficient handling of large datasets
* 🌐 User-friendly interface (Streamlit / Web-based)

---

## 🛠️ Tech Stack

* **Programming Language:** Python
* **Libraries:** Pandas, NumPy, Scikit-learn
* **Framework:** Streamlit (if used)
* **Version Control:** Git & GitHub

---

## 📂 Project Structure

```
Khojo/
│── app.py
│── model/
│── data/
│── README.md
│── requirements.txt
```

---

## 📊 Dataset

Due to GitHub's file size limitations (100MB), the dataset is hosted externally.

🔗 Download Dataset:
https://drive.google.com/file/d/1MNJYgDZQZxc2O-KZqdoBSdwD0hw9nkKZ/view

📌 After downloading, place the file in the project directory:

```
Khojo/
│── myntra.csv
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```
git clone https://github.com/Manvi9211/KHOJO.git
cd KHOJO
```

### 2️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 3️⃣ Run the application

```
streamlit run app.py
```

---

## 🧠 How It Works

1. Load dataset
2. Perform data preprocessing
3. Convert text/features into vectors
4. Compute similarity between products
5. Recommend similar items to users

---

## 📸 Screenshots

(Add screenshots of your project here)

---

## ⚠️ Note

* The dataset is not included in this repository due to size constraints.
* Please download it from the provided Google Drive link.

---

## 📌 Future Improvements

* 🔥 Add collaborative filtering
* 📱 Deploy as a web app
* 🧠 Improve recommendation accuracy using deep learning
* ☁️ Cloud deployment

---

## 👩‍💻 Author

**Manvi Mishra**

---

## ⭐ Acknowledgements

* Dataset source: Myntra dataset
* Libraries and tools used in development

---
