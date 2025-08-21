# Database Seeding Guide

This document explains how to populate your Sokoni e-commerce database with sample data for development and testing.

## Quick Start (Recommended)

For a complete setup with all sample data:

```bash
# Full development setup
python manage.py seed_dev

# Quick setup with smaller dataset
python manage.py seed_dev --small

# Clear existing data and reseed
python manage.py seed_dev --clear
```

**Note**: Products require users to exist first. The seeding commands handle this automatically, but if running individual commands, ensure users are created before products.

## Individual Seeders

You can also run individual seeders for more control:

### 1. Categories
```bash
# Create product categories and subcategories
python manage.py seed_categories

# Clear existing categories first
python manage.py seed_categories --clear
```

### 2. Users & Customers
```bash
# Create 25 users with customer profiles and addresses
python manage.py seed_users --count 25 --with-addresses

# Create only 10 users without addresses
python manage.py seed_users --count 10
```

### 3. Products
```bash
# Create 50 products with realistic data (assigned to random users)
python manage.py seed_products --count 50

# Clear existing products first
python manage.py seed_products --count 30 --clear
```

### 4. Coupons
```bash
# Create discount coupons
python manage.py seed_coupons

# Clear existing coupons first
python manage.py seed_coupons --clear
```

### 5. Complete Dataset
```bash
# Create everything (users, products, orders, reviews, payments)
python manage.py seed_all --users 20 --products 40 --orders 25

# Clear everything first
python manage.py seed_all --clear --users 15 --products 30 --orders 20
```

## What Gets Created

### 📂 Categories
- **8 main categories**: Electronics, Fashion, Home & Garden, Sports & Fitness, Books & Media, Health & Beauty, Automotive, Baby & Kids
- **50+ subcategories**: Each main category has 6-8 subcategories
- **Hierarchical structure**: Categories with parent-child relationships

### 👥 Users & Customers
- **Test users**: With Kenyan and international names
- **Customer profiles**: Complete with phone numbers, birth dates, preferences
- **Addresses**: Realistic Kenyan addresses (Nairobi, Mombasa, Kisumu, etc.)
- **Default password**: `password123` for all test users

### 🛍️ Products
- **Realistic products**: Category-appropriate items with real names and descriptions
- **User ownership**: Each product is assigned to a random user
- **Varied pricing**: From $10 to $3000+ depending on category
- **Stock levels**: Random stock quantities (0-100)
- **Product images**: Placeholder image paths
- **SKUs**: Unique product codes
- **Sale prices**: Some products have compare_at_price for discounts

### 🎫 Coupons
- **Welcome coupons**: For new customers (WELCOME10, NEWBIE20)
- **Percentage discounts**: 5% to 50% off
- **Fixed amount**: $5 to $150 off
- **Free shipping**: Various free shipping coupons
- **Category-specific**: Electronics, Fashion, etc.
- **Seasonal**: Holiday and special event coupons
- **Usage limits**: Realistic usage counts and limits

### 📦 Orders & Payments
- **Sample orders**: With realistic item combinations
- **Order statuses**: Pending, confirmed, processing, shipped, delivered, cancelled
- **Payment statuses**: Pending, paid, failed, refunded
- **Payment transactions**: Paystack integration records
- **Shipping addresses**: From customer address book
- **Order totals**: Calculated with tax and shipping

### ⭐ Reviews
- **Product reviews**: 1-5 star ratings with titles and comments
- **Verified purchases**: Mix of verified and unverified reviews
- **Realistic content**: Varied review text and ratings

## Sample Data Overview

| Data Type | Count (Full) | Count (Small) |
|-----------|--------------|---------------|
| Users | 25 | 10 |
| Addresses | 50-75 | 20-30 |
| Categories | 50+ | 50+ |
| Products | 50 | 25 |
| Coupons | 20+ | 20+ |
| Orders | 30 | 15 |
| Reviews | 80-150 | 40-75 |

## Sample Login Credentials

All test users have the password: **`password123`**

Sample usernames (generated dynamically):
- `wanjiku.kamau`
- `john.smith`
- `sarah.johnson`
- `michael.ochieng`

## Sample Coupon Codes

Try these coupon codes in your checkout:
- `WELCOME10` - 10% off for new customers
- `SAVE15` - 15% off orders over $100
- `FLAT50` - $50 off orders over $200
- `FREESHIP` - Free shipping over $25
- `ELECTRONICS20` - 20% off electronics

## Development Tips

1. **Start with seed_dev**: Use `python manage.py seed_dev` for quick setup
2. **Use --small for testing**: Faster database creation for quick tests
3. **Clear data**: Use `--clear` flag to reset before reseeding
4. **Check admin**: Visit `/admin/` to see all created data
5. **Test features**: Try cart, checkout, coupons, reviews, etc.

## Resetting Data

To completely reset and reseed:

```bash
# Option 1: Use clear flag
python manage.py seed_dev --clear

# Option 2: Manual reset
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_dev
```

## Kenyan Context

The seeders include Kenya-specific data:
- **Cities**: Nairobi, Mombasa, Kisumu, Nakuru, Eldoret, etc.
- **Phone numbers**: Kenyan mobile format (+254...)
- **Addresses**: Realistic Kenyan street names and areas
- **Counties**: All 47 Kenyan counties represented
- **Currency**: Prices in USD but suitable for KES conversion

## Troubleshooting

**Categories not found**: Run `python manage.py seed_categories` first

**Permission errors**: Ensure proper Django setup and database permissions

**Memory issues**: Use `--small` flag for limited resources

**Import errors**: Ensure all apps are in INSTALLED_APPS

For more help, check the individual seeder files in the `management/commands/` directories.
