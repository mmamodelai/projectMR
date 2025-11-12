# Leafly Scraper Documentation

## What It Does

The Leafly scraper is a Python tool that **extracts comprehensive cannabis strain data from Leafly.com** and saves it in a clean, structured JSON format ready for machine learning models, databases, and AI applications.

It scrapes **25+ data points** per strain including:
- Detailed descriptions (200-500 words)
- Effects, medical uses, and side effects
- Flavors, aromas, and terpenes
- Ratings and review counts
- THC/CBD/CBG percentages
- Parent strains and lineage
- Growing information
- High-quality images

---

## How It Works

### Architecture

```
1. Input: Strain names (from file or command line)
   ↓
2. HTTP Request: Fetch strain page from Leafly
   ↓
3. Parse HTML: Extract data using BeautifulSoup
   ↓
4. Multiple Strategies: Try different methods to find each field
   ↓
5. Validation: Verify data quality (e.g., THC < 40%)
   ↓
6. Output: Save to JSON file
```

### Data Extraction Strategy

The scraper uses **multiple fallback strategies** for robust data capture:

1. **JSON-LD structured data** (priority 1)
2. **Regex pattern matching** (priority 2)
3. **HTML element attributes** (priority 3)
4. **Keyword scanning** (priority 4)

**Example**: To find THC percentage, it tries:
- JSON-LD `"thc": "20%"`
- Regex `"THC: 20%"` or `"20% THC"`
- Data attributes `data-thc="20"`
- Parent/sibling text analysis

---

## Features

### ✨ Data Captured (25+ Fields)

**Core Identification:**
- `name` - Strain name
- `url` - Leafly URL
- `strain_type` - Indica, Sativa, or Hybrid
- `scraped_at` - ISO timestamp

**Text Content:**
- `description` - Full strain description (200-500 words)
- `aka` - Alternative names
- `lineage` - Parent cross information

**Effects & Medical:**
- `effects` - Array of effects (Relaxed, Euphoric, Creative...)
- `helps_with` - Array of medical uses (Anxiety, Pain, Insomnia...)
- `negatives` - Array of side effects (Dry mouth, Dizzy...)

**Sensory:**
- `flavors` - Array of taste notes (Pine, Citrus, Berry...)
- `aromas` - Array of smell notes (Earthy, Diesel, Floral...)
- `terpenes` - Array of terpenes (Limonene, Myrcene, Caryophyllene...)

**Ratings & Reviews:**
- `rating` - Average rating (1-5 stars)
- `review_count` - Number of user reviews

**Cannabinoids:**
- `thc_percent` - THC percentage (validated 0-40%)
- `cbd_percent` - CBD percentage (validated 0-25%)
- `cbg_percent` - CBG percentage (validated 0-5%)

**Genetics:**
- `parent_strains` - Array of parent strains
- `breeder` - Strain breeder/creator

**Growing Info:**
- `grow_difficulty` - Easy, Moderate, Difficult
- `flowering_time` - Days/weeks to flower

**Media:**
- `image_url` - High-quality strain image

---

## How to Use

### 1. Single Strain Scrape

```bash
cd leafly
python leafly_scraper.py "OG Kush"
```

**Output**: `og-kush.json`

### 2. Batch Scrape (Multiple Strains)

Create a text file with strain names (one per line):

```text
# strains.txt
OG Kush
Blue Dream
Sour Diesel
Girl Scout Cookies
```

Run batch scrape:

```bash
python leafly_scraper.py strains.txt output.json
```

**Output**: `output.json` (all strains in one file)

### 3. Using Batch Script (Windows)

```bash
scrape_leafly.bat
```

This will:
1. Create/activate virtual environment
2. Install dependencies
3. Run the scraper
4. Save results to `leafly_data.json`

---

## Installation

### Requirements

```bash
# Install Python 3.8+
# Then install dependencies:
pip install -r requirements_scraper.txt
```

**Dependencies** (`requirements_scraper.txt`):
```
beautifulsoup4>=4.12.0
requests>=2.31.0
lxml>=4.9.0
```

### File Structure

```
leafly/
├── leafly_scraper.py           # Main scraper script
├── requirements_scraper.txt    # Python dependencies
├── scrape_leafly.bat           # Windows batch runner
├── inventory_strains.txt       # List of strains to scrape
└── Data/
    ├── inventory_enhanced_v2.json    # Main dataset (31 strains)
    └── expansion_33_complete.json    # Expansion dataset (33 strains)
```

---

## Output Format

### JSON Structure

```json
{
  "name": "OG Kush",
  "url": "https://www.leafly.com/strains/og-kush",
  "strain_type": "Hybrid",
  "description": "OG Kush, also known as 'Premium OG Kush,' was first cultivated in Florida in the early '90s...",
  "rating": 4.28,
  "review_count": 5665,
  "thc_percent": 22.5,
  "cbd_percent": 0.5,
  "effects": [
    "Relaxed",
    "Euphoric",
    "Happy",
    "Uplifted",
    "Creative"
  ],
  "helps_with": [
    "Anxiety",
    "Stress",
    "Depression",
    "Pain",
    "Insomnia"
  ],
  "negatives": [
    "Dry mouth",
    "Dry eyes",
    "Paranoid"
  ],
  "flavors": [
    "Pine",
    "Diesel",
    "Citrus",
    "Lemon",
    "Earthy"
  ],
  "terpenes": [
    "Caryophyllene",
    "Limonene",
    "Myrcene"
  ],
  "parent_strains": [
    "Chemdawg",
    "Lemon Thai",
    "Hindu Kush"
  ],
  "lineage": "Chemdawg x Lemon Thai x Hindu Kush",
  "image_url": "https://images.leafly.com/flower-images/og-kush.png",
  "scraped_at": "2025-10-14T15:30:00.123456"
}
```

---

## Data Quality Features

### Validation
- **THC**: 0-40% (rejects outliers)
- **CBD**: 0-25% (rejects outliers)
- **CBG**: 0-5% (rejects outliers)
- **Duplicates**: Automatically detected and flagged

### Error Handling
- HTTP errors (404, timeout) are logged and skipped
- Unicode encoding errors are handled
- Missing data fields are set to `null` or empty arrays
- Real-time progress feedback during batch scraping

### Data Completeness
The scraper tracks field coverage:
```
✅ Name: 100% (24/24)
✅ Description: 100% (24/24)
✅ Type: 100% (24/24)
✅ Rating: 100% (24/24)
✅ Effects: 100% (24/24)
⚠️  THC%: 83% (20/24)
⚠️  Parent Strains: 67% (16/24)
```

---

## Advanced Features

### 1. Real-Time Feedback

During batch scraping, you get live updates:

```
Scraping batch of 31 strains...

[1/31] ✓ OG Kush (4.28★, 5665 reviews)
[2/31] ✓ Blue Dream (4.31★, 6892 reviews)
[3/31] ✗ Unknown Strain (404 Not Found)
[4/31] ✓ Sour Diesel (4.25★, 4103 reviews)
...

Summary:
- Scraped: 28/31 (90.3%)
- Failed: 3/31 (9.7%)
- Fields captured: 22 avg per strain
```

### 2. Deduplication

The scraper can detect and remove duplicate entries:

```bash
python clean_expansion_data.py
```

### 3. Data Analysis

Generate statistics on your scraped data:

```bash
python analyze_v2_data.py
```

**Output**:
- Field coverage percentages
- Sample data for each field
- Data quality metrics
- Missing data report

---

## Integration Examples

### Import to Database

**Python**:
```python
import json
from supabase import create_client

# Load scraped data
with open('Data/inventory_enhanced_v2.json', 'r', encoding='utf-8') as f:
    strains = json.load(f)

# Import to Supabase
supabase = create_client(url, key)
for strain in strains:
    supabase.table('leafly_strains').insert({
        'name': strain['name'],
        'description': strain['description'],
        'effects': strain['effects'],
        'rating': strain['rating']
    }).execute()
```

### Use in Machine Learning

```python
import pandas as pd

# Load data
df = pd.read_json('Data/inventory_enhanced_v2.json')

# Create feature vectors
X = pd.get_dummies(df['effects'].apply(pd.Series).stack()).groupby(level=0).sum()
y = df['strain_type']

# Train model
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier()
model.fit(X, y)
```

### Use in AI Chatbot

```python
# Search by effect
def find_strains_by_effect(effect, strains_data):
    return [
        s for s in strains_data 
        if effect in s.get('effects', [])
    ]

# Example
relaxing_strains = find_strains_by_effect('Relaxed', strains)
print(f"Found {len(relaxing_strains)} relaxing strains")
```

---

## Troubleshooting

### Common Issues

**1. 404 Errors**
```
Problem: Strain name not found on Leafly
Solution: Try alternative names (e.g., "Gorilla Glue #4" → "GG4")
```

**2. Unicode Errors**
```
Problem: Console can't display special characters
Solution: Script auto-handles this with UTF-8 encoding
```

**3. Missing Data**
```
Problem: Some fields are empty
Solution: Leafly pages vary in completeness - this is expected
```

**4. Timeout Errors**
```
Problem: Request takes too long
Solution: Increase timeout in script or check internet connection
```

---

## Best Practices

### Scraping Strategy

1. **Start small**: Test with 1-2 strains first
2. **Use batch files**: Organize strains by priority
3. **Verify names**: Check Leafly URLs before batch scraping
4. **Save incrementally**: Don't scrape everything at once
5. **Respect rate limits**: Add delays between requests (built-in)

### Data Management

1. **Version control**: Name outputs with dates (e.g., `scraped_2025_10_14.json`)
2. **Backup before merging**: Keep original files safe
3. **Validate after scraping**: Run analysis script to check quality
4. **Deduplicate regularly**: Run clean script after batch scrapes

---

## Version History

### v2.0 (Current)
- ✅ Enhanced data extraction (25+ fields)
- ✅ Multiple fallback strategies
- ✅ Data validation (THC/CBD/CBG)
- ✅ Real-time progress feedback
- ✅ Robust error handling
- ✅ Unicode support

### v1.0
- Basic scraping (10 fields)
- Single extraction strategy
- Limited error handling

---

## Performance

### Speed
- **Single strain**: ~2-3 seconds
- **Batch (30 strains)**: ~60-90 seconds
- **Rate limit**: ~0.5 seconds between requests

### Success Rate
- **Name/Description**: 100%
- **Type/Rating**: 100%
- **Effects/Flavors**: 100%
- **THC/CBD**: 80-85%
- **Parent Strains**: 65-70%
- **Growing Info**: 40-50%

### Data Quality
- **Field completeness**: 85% average
- **Validation pass rate**: 95%
- **Duplicate rate**: <1%

---

## Future Enhancements

**Potential improvements**:
- [ ] Add retry logic for failed requests
- [ ] Scrape strain photos (all sizes)
- [ ] Extract user reviews text
- [ ] Capture grow journal data
- [ ] Add proxy support for rate limiting
- [ ] Implement caching for repeated scrapes
- [ ] Add CLI arguments for custom output locations
- [ ] Support for other cannabis databases (Weedmaps, AllBud)

---

## Support

### Files
- **Main script**: `leafly/leafly_scraper.py`
- **Documentation**: `leafly/README.md`
- **Examples**: `leafly/ENHANCED_DATA_EXAMPLES.md`

### Data Locations
- **Main dataset**: `Data/inventory_enhanced_v2.json` (31 strains)
- **Expansion**: `Data/expansion_33_complete.json` (33 strains)

### Related Tools
- **Analysis**: `leafly/analyze_v2_data.py`
- **Deduplication**: `leafly/clean_expansion_data.py`
- **Database Import**: `leafly/supabase-integration/import_leafly_to_supabase.py`

---

## License & Ethics

### Usage Guidelines
- ✅ **Personal use**: Educational, research, business intelligence
- ✅ **Respect robots.txt**: Follow Leafly's scraping guidelines
- ✅ **Rate limiting**: Built-in delays to avoid overloading servers
- ⚠️ **Attribution**: Credit Leafly as data source
- ❌ **Redistribution**: Don't republish Leafly's content verbatim

### Data Source
All data is scraped from **Leafly.com** - the world's largest cannabis information resource.

---

**Created**: October 2025  
**Version**: 2.0  
**Status**: Production-ready  
**Maintainer**: MoTa CRM Project



