# Sales Data Report - Quick Guide

**Created**: November 7, 2025  
**Purpose**: Fetch sales data for specific dates from Blaze API database

---

## 📊 Requested Dates

- **Sept 25, 2025**
- **Oct 25, 2025**
- **Nov 1-5, 2025** (5 days)
- **Dec 24, 2024**

---

## 🗄️ Database Overview

Your Supabase database (`kiwmwoqrguyrcpjytgte.supabase.co`) contains **TWO sets** of transaction tables:

### 1. Original/CSV Tables (Historical)
- **Table**: `transactions`
- **Records**: 36,463 transactions
- **Date Range**: Jan 1 - Oct 9, 2025 (9 months)
- **Revenue**: ~$1.95M
- **Source**: CSV imports

### 2. Blaze API Tables (Live Data) ⭐ **RECOMMENDED**
- **Table**: `transactions_blaze`
- **Records**: 372,237 transactions (10x more!)
- **Date Range**: Historical + real-time
- **Auto-syncing**: Every 15 minutes via Edge Functions
- **Source**: Live Blaze POS system

**💡 Use `transactions_blaze` for most complete data**

---

## 🚀 How to Get Your Sales Data

### Option 1: Python Script (Easiest) ⭐

**Double-click**: `get_sales_data.bat`

or run in terminal:
```bash
python get_sales_data.py
```

**Output**:
- Formatted table in console
- CSV file: `sales_report_YYYYMMDD_HHMMSS.csv`
- Comparison of Blaze vs CSV data

**Sample Output**:
```
Date        | Transactions | Gross Sales  | Tax       | Discounts | Unique Customers
------------|-------------|--------------|-----------|-----------|------------------
2024-12-24  | 245         | $12,450.00   | $1,245.00 | $350.00   | 198
2025-09-25  | 312         | $18,920.00   | $1,892.00 | $420.00   | 256
2025-10-25  | 287         | $16,340.00   | $1,634.00 | $380.00   | 234
...
```

### Option 2: SQL Query (Direct Database)

1. Open **Supabase SQL Editor**: https://supabase.com/dashboard/project/kiwmwoqrguyrcpjytgte/sql
2. Copy query from: `sql_scripts/sales_data_report.sql`
3. Run the query section you need

**Available queries**:
- **Part 1**: Blaze API data (most complete)
- **Part 2**: CSV/historical data
- **Part 3**: Combined summary (both sources)
- **Part 4**: Hourly breakdown
- **Part 5**: Top products for these dates
- **Part 6**: Payment method breakdown

### Option 3: Supabase Dashboard (Visual)

1. Go to: https://supabase.com/dashboard/project/kiwmwoqrguyrcpjytgte/editor
2. Select `transactions_blaze` table
3. Add filters:
   - `date` >= `2025-09-25T00:00:00`
   - `date` <= `2025-09-25T23:59:59`
   - `blaze_status` = `Completed`
   - `total_amount` > `0`
4. View results

---

## 📈 What You'll Get

For each date, you'll see:

| Metric | Description |
|--------|-------------|
| **Transaction Count** | Total completed sales |
| **Gross Sales** | Total revenue before discounts |
| **Total Tax** | Tax collected |
| **Total Discounts** | Discounts applied |
| **Net Sales** | Gross - Discounts |
| **Unique Customers** | Number of different customers |
| **Avg Transaction** | Average sale amount |

---

## 🎯 Quick Start

**Fastest way to get your data:**

1. **Double-click**: `get_sales_data.bat`
2. Wait ~10 seconds
3. Get formatted report + CSV file

**That's it!** 🎉

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `get_sales_data.py` | Python script to fetch data |
| `get_sales_data.bat` | Windows launcher (double-click to run) |
| `sql_scripts/sales_data_report.sql` | SQL queries for Supabase |
| `SALES_DATA_GUIDE.md` | This guide |

---

## 🔍 Example Queries

### Get specific date
```sql
SELECT 
    COUNT(*) as transactions,
    SUM(total_amount) as gross_sales,
    AVG(total_amount) as avg_transaction
FROM transactions_blaze
WHERE DATE(date) = '2025-09-25'
    AND blaze_status = 'Completed'
    AND total_amount > 0;
```

### Get date range
```sql
SELECT 
    DATE(date) as sale_date,
    COUNT(*) as transactions,
    SUM(total_amount) as gross_sales
FROM transactions_blaze
WHERE DATE(date) BETWEEN '2025-11-01' AND '2025-11-05'
    AND blaze_status = 'Completed'
    AND total_amount > 0
GROUP BY DATE(date)
ORDER BY DATE(date);
```

---

## 💡 Tips

1. **For recent dates** (after Oct 9, 2025): Use `transactions_blaze` only
2. **For historical dates** (before Oct 9, 2025): Check both tables
3. **For December 2024**: Use `transactions_blaze` (historical backfill)
4. **Export to Excel**: Use the generated CSV file

---

## 🆘 Troubleshooting

**No data showing?**
- Check if date is formatted correctly: `YYYY-MM-DD`
- Verify transactions exist for that date
- Make sure using `transactions_blaze` (not `transactions`)

**Script not running?**
- Install requirements: `pip install pandas tabulate supabase`
- Check Python version: `python --version` (need 3.7+)

**Need different dates?**
- Edit `get_sales_data.py`
- Update `TARGET_DATES` list
- Re-run script

---

## 📞 Support

- **Database**: https://supabase.com/dashboard/project/kiwmwoqrguyrcpjytgte
- **Documentation**: `blaze-api-sync/README.md`
- **WORKLOG**: See entry [2025-11-07] Sales Data Report Generator

---

**Last Updated**: November 7, 2025  
**Status**: ✅ Ready to use



