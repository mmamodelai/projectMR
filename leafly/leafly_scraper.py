#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leafly Strain Scraper - Enhanced Version
Scrapes strain information from Leafly.com including images

Usage:
    python leafly_scraper.py "Gelato 41"
    python leafly_scraper.py --url "https://www.leafly.com/strains/gelato-41"
    python leafly_scraper.py --batch strains.txt
"""

import re
import sys
import io
import json
import argparse
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import quote
from datetime import datetime

# Fix Unicode encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class LeaflyScraper:
    """Scraper for extracting strain data from Leafly.com"""
    
    BASE_URL = "https://www.leafly.com"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    def __init__(self, timeout=10):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.timeout = timeout
    
    def strain_name_to_url(self, strain_name: str) -> str:
        """Convert strain name to Leafly URL"""
        # Clean strain name: lowercase, replace spaces/special chars with hyphens
        slug = strain_name.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars except hyphen
        slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces/multiple hyphens with single hyphen
        slug = slug.strip('-')
        
        return f"{self.BASE_URL}/strains/{slug}"
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse Leafly page"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_json_ld(self, soup: BeautifulSoup) -> Dict:
        """Extract JSON-LD structured data from page"""
        script_tag = soup.find('script', {'type': 'application/ld+json'})
        if script_tag:
            try:
                return json.loads(script_tag.string)
            except json.JSONDecodeError:
                pass
        return {}
    
    def scrape_strain(self, strain_name: str = None, url: str = None) -> Optional[Dict]:
        """
        Scrape strain information from Leafly
        
        Args:
            strain_name: Name of strain to search for
            url: Direct URL to Leafly strain page
            
        Returns:
            Dictionary with strain data or None if failed
        """
        if url:
            target_url = url
        elif strain_name:
            target_url = self.strain_name_to_url(strain_name)
        else:
            raise ValueError("Must provide either strain_name or url")
        
        print(f"Fetching: {target_url}")
        soup = self.fetch_page(target_url)
        
        if not soup:
            return None
        
        # Initialize data structure with ALL possible fields
        data = {
            'name': '',
            'aka': [],
            'url': target_url,
            'strain_type': '',
            'thc_percent': None,
            'cbd_percent': None,
            'cbg_percent': None,
            'rating': None,
            'review_count': 0,
            'effects': [],
            'helps_with': [],
            'negatives': [],
            'flavors': [],
            'aromas': [],
            'terpenes': [],
            'description': '',
            'parent_strains': [],
            'lineage': '',
            'image_url': '',
            'breeder': '',
            'grow_difficulty': '',
            'flowering_time': '',
            'reported_effects': {},
            'reported_flavors': {},
            'scraped_at': datetime.now().isoformat(),
        }
        
        # Try to get structured data first
        json_ld = self.extract_json_ld(soup)
        
        # Get full page text for pattern matching
        full_text = soup.get_text()
        
        # Extract strain name
        h1 = soup.find('h1')
        if h1:
            data['name'] = h1.get_text(strip=True)
        
        # Alternative: Check JSON-LD for name
        if not data['name'] and json_ld.get('name'):
            data['name'] = json_ld['name']
        
        # Extract "aka" (alternate names)
        aka_element = soup.find(string=re.compile(r'aka\s+', re.IGNORECASE))
        if aka_element:
            aka_text = aka_element.strip()
            # Extract text after "aka"
            match = re.search(r'aka\s+(.+)', aka_text, re.IGNORECASE)
            if match:
                data['aka'] = [name.strip() for name in match.group(1).split(',')]
        
        # Extract image URL (try multiple strategies)
        # Strategy 1: OpenGraph meta tag
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            data['image_url'] = og_image['content']
        
        # Strategy 2: Twitter card image
        if not data['image_url']:
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                data['image_url'] = twitter_image['content']
        
        # Strategy 3: Look for images with 'strain' in src/alt/class
        if not data['image_url']:
            img_tags = soup.find_all('img')
            for img in img_tags:
                src = img.get('src', '') or img.get('data-src', '')
                alt = img.get('alt', '').lower()
                classes = ' '.join(img.get('class', [])).lower()
                
                if any(keyword in src.lower() for keyword in ['strain', 'product', 'hero']):
                    if src and 'http' in src:
                        data['image_url'] = src
                        break
                elif 'strain' in alt or 'cannabis' in alt:
                    if src and 'http' in src:
                        data['image_url'] = src
                        break
        
        # Strategy 4: Look for JSON-LD image
        if not data['image_url'] and json_ld.get('image'):
            img_data = json_ld['image']
            if isinstance(img_data, str):
                data['image_url'] = img_data
            elif isinstance(img_data, dict) and img_data.get('url'):
                data['image_url'] = img_data['url']
            elif isinstance(img_data, list) and len(img_data) > 0:
                if isinstance(img_data[0], str):
                    data['image_url'] = img_data[0]
                elif isinstance(img_data[0], dict):
                    data['image_url'] = img_data[0].get('url', '')
        
        # Extract strain type (Hybrid, Indica, Sativa) - Multiple strategies
        # Strategy 1: Search text for explicit mention
        type_patterns = [
            r'(?:is an? )?(\bHybrid\b|\bIndica\b|\bSativa\b)',
            r'(?:Type|Strain)[:\s]*(\bHybrid\b|\bIndica\b|\bSativa\b)',
            r'(\bHybrid\b|\bIndica\b|\bSativa\b)\s+strain',
        ]
        for pattern in type_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                data['strain_type'] = match.group(1).capitalize()
                break
        
        # Strategy 2: Check for data attributes or aria-labels
        if not data['strain_type']:
            for type_name in ['Hybrid', 'Indica', 'Sativa']:
                elem = soup.find(attrs={'data-testid': lambda x: x and type_name.lower() in x.lower() if x else False})
                if elem:
                    data['strain_type'] = type_name
                    break
        
        # Extract THC/CBD/CBG percentages - Enhanced patterns
        # Strategy 1: Pattern like "THC: 24%" or "THC 24%"
        cannabinoid_patterns = [
            (r'THC[:\s]*(\d+\.?\d*)(?:\s*[-–]\s*\d+\.?\d*)?\s*%', 'thc_percent'),
            (r'CBD[:\s]*(\d+\.?\d*)(?:\s*[-–]\s*\d+\.?\d*)?\s*%', 'cbd_percent'),
            (r'CBG[:\s]*(\d+\.?\d*)(?:\s*[-–]\s*\d+\.?\d*)?\s*%', 'cbg_percent'),
        ]
        
        for pattern, key in cannabinoid_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    # Validation: THC typically 10-35%, CBD typically 0-20% for most strains
                    if key == 'thc_percent' and (value < 0 or value > 40):
                        continue  # Skip suspicious THC values
                    if key == 'cbd_percent' and value > 25:
                        continue  # Skip suspicious CBD values (high-CBD strains rare)
                    if key == 'cbg_percent' and value > 5:
                        continue  # CBG is usually <3%
                    data[key] = value
                except (ValueError, IndexError):
                    pass
        
        # Strategy 2: Look for structured data in JSON-LD or data attributes
        if json_ld:
            for cannabinoid in ['thc', 'cbd', 'cbg']:
                if json_ld.get(f'{cannabinoid}Percent'):
                    value = float(json_ld[f'{cannabinoid}Percent'])
                    # Apply same validation
                    if cannabinoid == 'thc' and (value < 0 or value > 40):
                        continue
                    if cannabinoid == 'cbd' and value > 25:
                        continue
                    if cannabinoid == 'cbg' and value > 5:
                        continue
                    data[f'{cannabinoid}_percent'] = value
        
        # Strategy 3: Search for spans/divs with specific classes or data attributes
        for cannabinoid in ['THC', 'CBD', 'CBG']:
            elements = soup.find_all(string=re.compile(cannabinoid, re.IGNORECASE))
            for elem in elements:
                parent = elem.parent
                if parent:
                    # Look for percentage in parent or sibling
                    parent_text = parent.get_text()
                    match = re.search(r'(\d+\.?\d*)\s*%', parent_text)
                    if match:
                        key = f'{cannabinoid.lower()}_percent'
                        if not data[key]:  # Only set if not already found
                            try:
                                value = float(match.group(1))
                                # Apply validation
                                if cannabinoid == 'THC' and (value < 0 or value > 40):
                                    continue
                                if cannabinoid == 'CBD' and value > 25:
                                    continue
                                if cannabinoid == 'CBG' and value > 5:
                                    continue
                                data[key] = value
                                break
                            except ValueError:
                                pass
        
        # Extract rating - Multiple strategies
        # Strategy 1: Search for JSON-LD aggregateRating
        if json_ld.get('aggregateRating'):
            rating_data = json_ld['aggregateRating']
            if isinstance(rating_data, dict):
                if rating_data.get('ratingValue'):
                    data['rating'] = float(rating_data['ratingValue'])
                if rating_data.get('reviewCount'):
                    data['review_count'] = int(rating_data['reviewCount'])
        
        # Strategy 2: Look for numeric pattern like "4.6"
        if not data['rating']:
            # Search for ratings pattern (typically X.X out of 5)
            rating_patterns = [
                r'(\d+\.\d+)\s*(?:out of|\/)\s*5',
                r'rating[:\s]*(\d+\.\d+)',
                r'(\d+\.\d+)\s*stars?',
            ]
            for pattern in rating_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    try:
                        rating_value = float(match.group(1))
                        if 0 <= rating_value <= 5:  # Validate rating range
                            data['rating'] = rating_value
                            break
                    except ValueError:
                        pass
        
        # Strategy 3: Look for star rating elements
        if not data['rating']:
            rating_elem = soup.find(attrs={'itemprop': 'ratingValue'})
            if rating_elem:
                try:
                    data['rating'] = float(rating_elem.get_text(strip=True))
                except ValueError:
                    pass
        
        # Extract review count - Multiple strategies
        # Strategy 1: Pattern like "1,234 ratings" or "1234 reviews"
        if not data['review_count']:
            review_patterns = [
                r'([\d,]+)\s*(?:ratings?|reviews?)',
                r'(?:ratings?|reviews?)[:\s]*([\d,]+)',
                r'([\d,]+)\s*people\s+rated',
            ]
            for pattern in review_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    try:
                        count_str = match.group(1).replace(',', '')
                        data['review_count'] = int(count_str)
                        break
                    except ValueError:
                        pass
        
        # Strategy 2: Look for reviewCount attribute
        if not data['review_count']:
            review_elem = soup.find(attrs={'itemprop': 'reviewCount'})
            if review_elem:
                try:
                    data['review_count'] = int(review_elem.get_text(strip=True).replace(',', ''))
                except ValueError:
                    pass
        
        # Extract effects (look for common effect keywords)
        effects_keywords = [
            'Relaxed', 'Aroused', 'Tingly', 'Euphoric', 'Happy', 'Uplifted',
            'Energetic', 'Creative', 'Focused', 'Giggly', 'Sleepy', 'Hungry',
            'Talkative', 'Calm', 'Focused', 'Alert'
        ]
        for keyword in effects_keywords:
            if soup.find(string=re.compile(rf'\b{keyword}\b', re.IGNORECASE)):
                if keyword not in data['effects']:
                    data['effects'].append(keyword)
        
        # Extract "Helps with" conditions
        helps_keywords = [
            'Anxiety', 'Stress', 'Depression', 'Pain', 'Insomnia', 'Fatigue',
            'Lack of appetite', 'Nausea', 'Inflammation', 'Muscle spasms',
            'Migraines', 'Headaches', 'Cramps', 'PTSD'
        ]
        for keyword in helps_keywords:
            if soup.find(string=re.compile(rf'\b{keyword}\b', re.IGNORECASE)):
                if keyword not in data['helps_with']:
                    data['helps_with'].append(keyword)
        
        # Extract negative effects
        negative_keywords = [
            'Dry mouth', 'Dry eyes', 'Paranoid', 'Anxious', 'Dizzy', 'Headache'
        ]
        for keyword in negative_keywords:
            if soup.find(string=re.compile(rf'\b{keyword}\b', re.IGNORECASE)):
                if keyword not in data['negatives']:
                    data['negatives'].append(keyword)
        
        # Extract flavors and aromas
        flavor_keywords = [
            'Lavender', 'Pepper', 'Flowery', 'Earthy', 'Pine', 'Diesel',
            'Citrus', 'Lemon', 'Berry', 'Grape', 'Sweet', 'Spicy', 'Mint',
            'Vanilla', 'Butter', 'Fruity', 'Tropical', 'Sour', 'Woody',
            'Pungent', 'Skunk', 'Chemical', 'Ammonia', 'Tree Fruit', 'Apple',
            'Apricot', 'Peach', 'Pear', 'Orange', 'Grapefruit', 'Blueberry',
            'Strawberry', 'Cheese', 'Tar', 'Tobacco', 'Menthol', 'Nutty',
            'Coffee', 'Tea', 'Honey', 'Rose', 'Violet'
        ]
        for keyword in flavor_keywords:
            if soup.find(string=re.compile(rf'\b{keyword}\b', re.IGNORECASE)):
                if keyword not in data['flavors']:
                    data['flavors'].append(keyword)
                if keyword not in data['aromas']:
                    data['aromas'].append(keyword)
        
        # Extract terpenes
        terpene_keywords = [
            'Caryophyllene', 'Limonene', 'Myrcene', 'Linalool', 'Pinene',
            'Humulene', 'Terpinolene', 'Ocimene', 'Bisabolol', 'Valencene',
            'Geraniol', 'Eucalyptol', 'Nerolidol', 'Phytol'
        ]
        for keyword in terpene_keywords:
            if soup.find(string=re.compile(rf'\b{keyword}\b', re.IGNORECASE)):
                if keyword not in data['terpenes']:
                    data['terpenes'].append(keyword)
        
        # Extract description (look for paragraph with substantial text)
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 100:  # Substantial paragraph
                data['description'] = text
                break
        
        # Extract parent strains (lineage) - Enhanced patterns
        lineage_patterns = [
            r'(?:is\s+)?(?:made\s+by\s+)?crossing\s+([A-Z][^\.,]+?)\s+(?:with|and)\s+([A-Z][^\.,]+?)[\.\,]',
            r'(?:is\s+)?(?:a\s+)?cross\s+(?:between|of)\s+([A-Z][^\.,]+?)\s+(?:with|and|x|×)\s+([A-Z][^\.,]+?)[\.\,]',
            r'made\s+(?:by|from)\s+(?:crossing|breeding)\s+([A-Z][^\.,]+?)\s+(?:with|and|x|×)\s+([A-Z][^\.,]+?)[\.\,]',
            r'blend\s+of\s+([A-Z][^\.,]+?)\s+(?:and|x|×)\s+([A-Z][^\.,]+?)[\.\,]',
            r'(?:parents?|lineage)[:\s]+([A-Z][^\.,x×]+?)\s+(?:and|x|×)\s+([A-Z][^\.,]+?)[\.\,]',
        ]
        
        for pattern in lineage_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                parent1 = match.group(1).strip()
                parent2 = match.group(2).strip()
                # Clean up parent names (remove trailing words like "strain")
                parent1 = re.sub(r'\s+strain$', '', parent1, flags=re.IGNORECASE).strip()
                parent2 = re.sub(r'\s+strain$', '', parent2, flags=re.IGNORECASE).strip()
                
                if parent1 and parent2 and len(parent1) > 2 and len(parent2) > 2:
                    data['parent_strains'] = [parent1, parent2]
                    data['lineage'] = f"{parent1} x {parent2}"
                    break
        
        # Alternative: Look for structured data in JSON-LD
        if not data['parent_strains'] and json_ld:
            if json_ld.get('parents'):
                parents = json_ld['parents']
                if isinstance(parents, list) and len(parents) >= 2:
                    data['parent_strains'] = parents[:2]
                    data['lineage'] = f"{parents[0]} x {parents[1]}"
        
        # Extract breeder information
        breeder_patterns = [
            r'bred\s+by\s+([^\.]+?)[\.\,]',
            r'breeder[:\s]+([^\.]+?)[\.\,]',
            r'created\s+by\s+([^\.]+?)[\.\,]'
        ]
        for pattern in breeder_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                data['breeder'] = match.group(1).strip()
                break
        
        # Extract grow info
        if 'difficult' in full_text.lower():
            if 'easy' in full_text.lower():
                data['grow_difficulty'] = 'Easy'
            elif 'moderate' in full_text.lower():
                data['grow_difficulty'] = 'Moderate'
            else:
                data['grow_difficulty'] = 'Difficult'
        
        # Extract flowering time
        flowering_match = re.search(r'(\d+)[-\s](\d+)\s*(?:weeks?|days?)', full_text, re.IGNORECASE)
        if flowering_match:
            data['flowering_time'] = f"{flowering_match.group(1)}-{flowering_match.group(2)} weeks"
        
        return data
    
    def print_data_summary(self, data: Dict):
        """Print a summary of what was captured"""
        captured = []
        missing = []
        
        checks = [
            ('name', 'Name'),
            ('strain_type', 'Type'),
            ('thc_percent', 'THC%'),
            ('cbd_percent', 'CBD%'),
            ('rating', 'Rating'),
            ('review_count', 'Reviews'),
            ('image_url', 'Image'),
            ('parent_strains', 'Parents'),
            ('description', 'Description'),
        ]
        
        for key, label in checks:
            value = data.get(key)
            if value and value != [] and value != 0:
                captured.append(label)
            else:
                missing.append(label)
        
        print(f"  ✅ Captured: {', '.join(captured)}")
        if missing:
            print(f"  ❌ Missing: {', '.join(missing)}")
    
    def scrape_batch(self, strain_names: List[str]) -> List[Dict]:
        """Scrape multiple strains"""
        results = []
        for i, name in enumerate(strain_names, 1):
            print(f"\n[{i}/{len(strain_names)}] Scraping: {name}")
            data = self.scrape_strain(strain_name=name)
            if data:
                self.print_data_summary(data)
                results.append(data)
            else:
                print(f"  ❌ Failed to scrape {name}")
        return results
    
    def export_to_json(self, data: List[Dict], output_file: str):
        """Export scraped data to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Exported {len(data)} strains to {output_file}")
    
    def export_to_csv(self, data: List[Dict], output_file: str):
        """Export scraped data to CSV file"""
        import csv
        
        if not data:
            print("No data to export")
            return
        
        # Flatten data for CSV
        fieldnames = [
            'name', 'aka', 'strain_type', 'thc_percent', 'cbd_percent', 'cbg_percent',
            'rating', 'review_count', 'effects', 'flavors', 'terpenes',
            'description', 'parent_strains', 'lineage', 'url'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in data:
                # Convert lists to comma-separated strings
                row_copy = row.copy()
                for key in ['aka', 'effects', 'flavors', 'terpenes', 'parent_strains']:
                    if isinstance(row_copy.get(key), list):
                        row_copy[key] = ', '.join(row_copy[key])
                writer.writerow(row_copy)
        
        print(f"\n✅ Exported {len(data)} strains to {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Scrape strain data from Leafly')
    parser.add_argument('strain', nargs='?', help='Strain name to scrape')
    parser.add_argument('--url', help='Direct URL to Leafly strain page')
    parser.add_argument('--batch', help='File with list of strain names (one per line)')
    parser.add_argument('--output', '-o', help='Output file (JSON or CSV)', default='leafly_strains.json')
    parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Output format')
    
    args = parser.parse_args()
    
    scraper = LeaflyScraper()
    
    # Batch mode
    if args.batch:
        with open(args.batch, 'r', encoding='utf-8') as f:
            strain_names = [line.strip() for line in f if line.strip()]
        
        print(f"📋 Batch scraping {len(strain_names)} strains...")
        results = scraper.scrape_batch(strain_names)
        
        if args.format == 'json':
            scraper.export_to_json(results, args.output)
        else:
            scraper.export_to_csv(results, args.output)
        
        return
    
    # Single strain mode
    if args.url:
        data = scraper.scrape_strain(url=args.url)
    elif args.strain:
        data = scraper.scrape_strain(strain_name=args.strain)
    else:
        parser.print_help()
        return
    
    if data:
        print("\n" + "="*60)
        print(f"✅ Scraped: {data['name']}")
        print("="*60)
        print(json.dumps(data, indent=2))
        
        # Save to file
        if args.output:
            if args.format == 'json':
                scraper.export_to_json([data], args.output)
            else:
                scraper.export_to_csv([data], args.output)
    else:
        print("\n❌ Failed to scrape strain data")


if __name__ == "__main__":
    main()

