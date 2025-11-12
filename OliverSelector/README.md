# OliverSelector - Customer Data Simulator

A fun UI tool for analyzing customer data, visualizing utility curves, and generating personalized SMS campaigns with AI training feedback.

## Features

### 🎯 Customer Overview
- **Customer Information**: Name, phone, email
- **Key Metrics**: Lifetime Value, Average Value per Visit, Visits per Month, Last Visit
- **Utility Curve**: Visual representation of customer engagement over time
- **Customer Selector**: Load different customers for analysis

### 📊 Purchase History
- Complete transaction history in an easy-to-read table
- Product details, categories, quantities, and pricing
- Sortable columns for easy analysis

### 📱 SMS Generator
- **3 AI-Generated Options**: Based on customer behavior patterns and contact urgency
- **Numpad Selection**: Use numpad keys 1, 2, 3 for quick selection
- **Custom Text Input**: Write your own personalized message
- **Contact Urgency Curve**: Visual guide for optimal contact timing
- **One-Click Selection**: Choose from generated options or custom text

### 🤖 AI Training
- **Feedback System**: Add notes about text effectiveness
- **Training Data Export**: Save selections and feedback for AI learning
- **Pattern Recognition**: Help improve future SMS generation

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the simulator:
```bash
python customer_simulator.py
```

## Usage

### Loading Customers
- Click "Load Random Customer" to cycle through sample data
- Customer metrics and utility curve update automatically
- Purchase history displays in the second tab

### Generating SMS
- Click "Generate New SMS Options" to create 3 personalized texts
- Options are based on:
  - Days since last visit
  - Customer lifetime value
  - Purchase patterns
  - Engagement score

### Selecting and Sending
- Click "Select #1", "#2", or "#3" to choose a generated option
- Or write custom text in the text area and click "Use Custom Text"
- Click "SEND SMS" to send the selected message

### AI Training
- Add feedback notes about why you selected a particular text
- Click "Save Training Data" to export for AI learning
- Data includes customer metrics, selected text, and your feedback

## Customer Metrics Explained

### Lifetime Value (LTV)
Total amount spent by the customer over their entire relationship with your business.

### Average Value per Visit
Total LTV divided by number of visits - shows spending consistency.

### Visits per Month
Average frequency of customer visits - indicates engagement level.

### Contact Urgency Curve
Shows when to contact customers based on their shopping patterns:
- **Low urgency** (0.0-0.3): Just visited or within normal pattern
- **Building urgency** (0.3-0.6): Approaching usual shopping day
- **Peak urgency** (0.6-0.9): Past due for visit - HIGH contact value
- **Declining urgency** (0.3-0.0): Too long without contact - potential churn

## SMS Strategy by Customer Type

### Recent Customers (0-7 days)
- Focus on retention and upselling
- Highlight new products matching their preferences
- Offer loyalty point bonuses

### Moderate Lapse (8-21 days)
- Re-engagement campaigns
- Remind about loyalty benefits
- Offer moderate discounts

### Long Lapse (22+ days)
- Win-back campaigns
- Significant discounts or special offers
- Emphasize VIP treatment and lifetime value

## Integration

The simulator is designed to integrate with:
- **Supabase Database**: Real customer data
- **SMS System**: Direct message sending
- **AI Training Pipeline**: Feedback data for model improvement

## Future Enhancements

- Real-time customer data from Supabase
- Advanced AI text generation with GPT integration
- A/B testing framework for SMS campaigns
- Customer segmentation and targeting
- Automated send timing optimization

## Architecture

Built with:
- **Python 3.8+**
- **Tkinter**: GUI framework
- **Matplotlib**: Data visualization
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations

Perfect for analyzing customer behavior and optimizing SMS marketing campaigns! 🚀
