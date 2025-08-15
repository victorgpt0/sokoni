# 🛍️ Sokoni - Kenyan E-commerce Platform

A modern, full-featured e-commerce web application built with Django, designed specifically for the Kenyan market. Sokoni (Swahili for "marketplace") provides a complete online shopping experience with user authentication, product management, shopping cart, order processing, and payment integration.

## ✨ Features

### 🛒 Core E-commerce
- **Product Catalog**: Browse products by categories with search and filtering
- **Shopping Cart**: Session-based cart with quantity management
- **User Accounts**: Registration, login, profile management
- **Order Management**: Complete order lifecycle with status tracking
- **Payment Integration**: Paystack payment gateway integration
- **Coupon System**: Discount codes and promotional offers

### 👤 User Features
- **Customer Profiles**: Extended user profiles with preferences
- **Address Management**: Multiple shipping addresses
- **Order History**: Complete order tracking and history
- **Product Reviews**: Rating and review system
- **Wishlist**: Save favorite products

### 🎨 Modern UI/UX
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Modern Components**: Reusable UI components
- **Smooth Animations**: Enhanced user experience
- **Clean Layout**: Professional and intuitive interface

### 🔧 Technical Features
- **Django 5.2**: Latest Django framework
- **PostgreSQL**: Production-ready database
- **REST API**: Django REST Framework for mobile apps
- **Image Processing**: Automatic image optimization
- **Search & Filtering**: Advanced product discovery
- **Audit Trail**: Complete activity logging

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- Virtual environment

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sokoni
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Seed the database** (optional)
   ```bash
   # Quick development setup
   python manage.py seed_dev
   
   # Or for smaller dataset
   python manage.py seed_dev --small
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Visit the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## 📁 Project Structure

```
sokoni/
├── accounts/           # User authentication & profiles
├── products/           # Product catalog & management
├── cart/              # Shopping cart functionality
├── orders/            # Order processing & management
├── payments/          # Payment integration (Paystack)
├── coupons/           # Discount & coupon system
├── templates/         # Django templates
│   ├── layouts/       # Base layouts
│   └── components/    # Reusable components
├── static/            # Static files (CSS, JS, images)
├── media/             # User-uploaded files
├── sokoni/            # Main project settings
└── manage.py          # Django management script
```

## 🛠️ Apps Overview

### Accounts App
- User registration and authentication
- Customer profile management
- Address management
- Order history
- Password management

### Products App
- Product catalog with categories
- Product images and variants
- Search and filtering
- Product reviews and ratings
- Inventory management

### Cart App
- Session-based shopping cart
- Quantity management
- Cart persistence
- Global cart context

### Orders App
- Order creation and processing
- Order status tracking
- Shipping address management
- Order history and details

### Payments App
- Paystack payment integration
- Payment verification
- Webhook handling
- Transaction logging

### Coupons App
- Discount code management
- Coupon validation
- Usage tracking
- Multiple discount types

## 🎨 Styling & UI

### Tailwind CSS
The project uses Tailwind CSS for styling with a custom color palette:
- **Primary**: `#4B0082` (Deep Purple)
- **Secondary**: `#E5E4E2` (Light Gray)

### Components
Reusable UI components are located in `templates/components/`:
- Form fields with consistent styling
- Navigation elements
- Product cards
- Order summaries

### Layouts
Base layouts in `templates/layouts/`:
- `base.html`: Main layout with navigation and footer
- Responsive design for all screen sizes

## 🔧 Configuration

### Environment Variables
Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sokoni

# Payment (Paystack)
PAYSTACK_PUBLIC_KEY=your-paystack-public-key
PAYSTACK_SECRET_KEY=your-paystack-secret-key

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Configuration
The project is configured to use PostgreSQL by default. Update your `DATABASE_URL` in the `.env` file:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

## 📊 Database Seeding

For development and testing, you can populate the database with sample data:

```bash
# Complete setup with all data
python manage.py seed_dev

# Quick setup with smaller dataset
python manage.py seed_dev --small

# Clear existing data and reseed
python manage.py seed_dev --clear
```

**Sample Data Includes:**
- 8 product categories with subcategories
- 25+ test users with profiles
- 50+ sample products with images
- 15+ discount coupons
- Sample orders and reviews

**Test Credentials:**
- **Admin**: `admin@example.com` / `admin123`
- **Customer**: `john.doe@example.com` / `password123`

For detailed seeding information, see [SEEDING.md](SEEDING.md).

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False` in production
- [ ] Configure production database
- [ ] Set up static file serving
- [ ] Configure email settings
- [ ] Set up SSL certificate
- [ ] Configure Paystack production keys
- [ ] Set up monitoring and logging

### Recommended Deployment Options
- **Heroku**: Easy deployment with PostgreSQL add-on
- **DigitalOcean**: App Platform or Droplet with Docker
- **AWS**: EC2 with RDS for database
- **Railway**: Simple deployment with automatic scaling

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test products
python manage.py test cart
```

## 📚 API Documentation

The project includes Django REST Framework with automatic API documentation:

```bash
# Start the development server
python manage.py runserver

# Visit API documentation
http://localhost:8000/api/docs/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the [documentation](docs/)
- Review the [SEEDING.md](SEEDING.md) for database setup

## 🙏 Acknowledgments

- Django community for the excellent framework
- Tailwind CSS for the utility-first CSS framework
- Paystack for payment integration
- All contributors and testers

---

**Built with ❤️ for the Kenyan e-commerce ecosystem**
