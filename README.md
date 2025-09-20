# 🛍️ Sokoni - Kenyan E-commerce Platform

A modern e-commerce web application built with Django, designed specifically for the Kenyan market. Sokoni (Swahili for "marketplace") provides a complete online shopping experience with user authentication, product management, shopping cart, order processing, and payment integration.

This is a project built purposefully for demonstration of DevOps knowledge and know how

## 🚀 Developer Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- Virtual environment

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/victorgpt0/sokoni.git
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


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

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
