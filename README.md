# SmoothBooks - Complete Accounting Software

A production-ready accounting software with invoicing, expense tracking, payroll integration, tax preparation, and user-friendly dashboards.

## Features

### ✅ Implemented
- **User Authentication**: JWT-based login/register system
- **Dashboard**: Real-time financial metrics and charts
- **Invoicing & Billing**: Complete invoice management system
- **Expense Tracking**: Categorize and track business expenses
- **Payroll Integration**: Employee management and payroll processing
- **Tax Preparation**: Financial and tax reporting
- **Mobile & Cloud Access**: Responsive web application
- **User-Friendly Dashboards**: Modern Material-UI interface

### 🔄 In Progress
- Advanced invoice templates
- PDF generation
- Email notifications
- Advanced reporting features

## Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite (production-ready, can migrate to PostgreSQL)
- **Authentication**: JWT tokens
- **API**: RESTful endpoints
- **ORM**: SQLAlchemy

### Frontend
- **Framework**: React 18
- **UI Library**: Material-UI (MUI)
- **Charts**: Recharts
- **Routing**: React Router
- **HTTP Client**: Axios

## Project Structure

```
SmoothBooks/
├── backend/                 # Flask API
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   ├── env.example         # Environment variables template
│   ├── models/             # Database models
│   │   ├── user.py         # User authentication
│   │   ├── invoice.py      # Invoicing system
│   │   ├── expense.py      # Expense tracking
│   │   └── payroll.py      # Payroll management
│   └── routes/             # API endpoints
│       ├── auth.py         # Authentication routes
│       ├── invoices.py     # Invoice management
│       ├── expenses.py     # Expense management
│       ├── payroll.py      # Payroll processing
│       ├── reports.py      # Financial reports
│       └── dashboard.py    # Dashboard data
├── frontend/               # React application
│   ├── package.json        # Node.js dependencies
│   ├── Dockerfile          # Frontend Docker configuration
│   ├── nginx.conf          # Nginx configuration
│   ├── public/             # Static files
│   └── src/                # React source code
│       ├── components/     # Reusable components
│       ├── pages/          # Page components
│       ├── contexts/       # React contexts
│       └── App.js          # Main application
├── .github/                # GitHub configuration
│   └── workflows/          # CI/CD workflows
│       └── ci.yml          # GitHub Actions pipeline
├── .gitignore              # Git ignore rules
├── .dockerignore           # Docker ignore rules
├── CONTRIBUTING.md         # Contributing guidelines
├── DEPLOYMENT.md           # Deployment guide
├── Dockerfile              # Backend Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── LICENSE                 # MIT License
├── README.md               # This file
├── setup.py                # Automated setup script
├── start.bat               # Windows start script
└── start.sh                # Unix/Linux/macOS start script
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Option 1: Automated Setup (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/samaron123/SmoothBooks.git
   cd SmoothBooks
   ```

2. **Run the setup script**:
   ```bash
   python setup.py
   ```

3. **Start the application**:
   ```bash
   # Windows
   start.bat
   
   # Unix/Linux/macOS
   ./start.sh
   ```

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd SmoothBooks/backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run the Flask server**:
   ```bash
   python app.py
   ```

The backend will start on `http://localhost:5000`

#### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd SmoothBooks/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the React development server**:
   ```bash
   npm start
   ```

The frontend will start on `http://localhost:3000`

### Option 3: Docker Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/samaron123/SmoothBooks.git
   cd SmoothBooks
   ```

2. **Set environment variables**:
   ```bash
   cp backend/env.example .env
   # Edit .env with your configuration
   ```

3. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend: http://localhost
   - Backend API: http://localhost:5000

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile

### Invoices
- `GET /api/invoices/` - List invoices
- `POST /api/invoices/` - Create invoice
- `GET /api/invoices/{id}` - Get invoice details
- `PUT /api/invoices/{id}` - Update invoice
- `DELETE /api/invoices/{id}` - Delete invoice

### Expenses
- `GET /api/expenses/` - List expenses
- `POST /api/expenses/` - Create expense
- `GET /api/expenses/{id}` - Get expense details
- `PUT /api/expenses/{id}` - Update expense
- `DELETE /api/expenses/{id}` - Delete expense

### Payroll
- `GET /api/payroll/employees` - List employees
- `POST /api/payroll/employees` - Create employee
- `GET /api/payroll/payroll` - List payroll records
- `POST /api/payroll/payroll` - Create payroll record

### Reports
- `GET /api/reports/financial-summary` - Financial summary
- `GET /api/reports/tax-summary` - Tax summary
- `GET /api/reports/export/csv` - Export CSV reports

### Dashboard
- `GET /api/dashboard/overview` - Dashboard overview
- `GET /api/dashboard/charts/revenue` - Revenue chart data
- `GET /api/dashboard/charts/expenses` - Expense chart data

## Database Schema

### Core Tables
- **users**: User accounts and authentication
- **invoices**: Invoice records with line items
- **payments**: Payment tracking for invoices
- **expenses**: Expense records with categories
- **employees**: Employee information
- **payroll_records**: Payroll processing records
- **time_entries**: Time tracking for employees

## Features in Detail

### 1. Invoicing & Billing
- Create professional invoices with line items
- Automatic tax calculations
- Multiple payment methods tracking
- Invoice status management (draft, sent, paid, overdue)
- Client management

### 2. Expense Tracking
- Categorize expenses by type
- Receipt upload support
- Expense approval workflow
- Payment method tracking
- Vendor management

### 3. Payroll Integration
- Employee profile management
- Time tracking and attendance
- Automatic payroll calculations
- Tax deductions and withholdings
- Payroll reports

### 4. Tax Preparation
- Financial summary reports
- Tax year summaries
- Export capabilities for tax filing
- Deduction tracking

### 5. Dashboard & Analytics
- Real-time financial metrics
- Revenue vs expense charts
- Monthly trend analysis
- Outstanding invoice tracking
- Quick stats overview

## Security Features

- JWT-based authentication
- Password hashing with Werkzeug
- CORS configuration
- Input validation and sanitization
- SQL injection protection via SQLAlchemy

## Deployment

SmoothBooks can be deployed using various methods:

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Cloud Deployment
- **Heroku**: See [DEPLOYMENT.md](DEPLOYMENT.md#heroku)
- **AWS**: See [DEPLOYMENT.md](DEPLOYMENT.md#aws-ec2--rds)
- **Google Cloud**: See [DEPLOYMENT.md](DEPLOYMENT.md#google-cloud-platform)

### Production Considerations
- Use strong secret keys
- Enable HTTPS/SSL
- Set up database backups
- Configure monitoring and logging
- Use production database (PostgreSQL)

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Development

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality
- Backend: Follow PEP 8 style guidelines
- Frontend: Use ESLint configuration
- Add tests for new features
- Update documentation

### CI/CD Pipeline
The project includes GitHub Actions workflows for:
- Automated testing
- Code quality checks
- Security scanning
- Dependency updates

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Start for Contributors
1. Fork the repository
2. Create a feature branch
3. Set up development environment
4. Make your changes
5. Add tests
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/samaron123/SmoothBooks/issues)
- **Discussions**: [GitHub Discussions](https://github.com/samaron123/SmoothBooks/discussions)
- **Documentation**: [README.md](README.md) and [DEPLOYMENT.md](DEPLOYMENT.md)

## Roadmap

### Upcoming Features
- [ ] Advanced invoice templates
- [ ] PDF generation
- [ ] Email notifications
- [ ] Advanced reporting features
- [ ] Mobile app
- [ ] Multi-tenant support
- [ ] API rate limiting
- [ ] Real-time notifications

### Recent Updates
- ✅ Complete accounting system
- ✅ User authentication
- ✅ Invoice management
- ✅ Expense tracking
- ✅ Payroll integration
- ✅ Financial reporting
- ✅ Modern React UI
- ✅ Docker support
- ✅ CI/CD pipeline

---

**SmoothBooks** - Making accounting simple and efficient for businesses of all sizes. 🚀 