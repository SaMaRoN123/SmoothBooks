# Contributing to SmoothBooks

Thank you for your interest in contributing to SmoothBooks! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)
- [Code of Conduct](#code-of-conduct)

## Getting Started

Before contributing, please:

1. Fork the repository
2. Create a feature branch from `main`
3. Set up your development environment
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Git

### Quick Setup

1. **Clone your fork**:
   ```bash
   git clone https://github.com/samaron123/SmoothBooks.git
   cd SmoothBooks
   ```

2. **Run the setup script**:
   ```bash
   python setup.py
   ```

3. **Start the development servers**:
   ```bash
   # Windows
   start.bat
   
   # Unix/Linux/macOS
   ./start.sh
   ```

### Manual Setup

If you prefer manual setup:

#### Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Unix/Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
cp env.example .env
# Edit .env with your configuration
python app.py
```

#### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## Code Style

### Python (Backend)

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Use type hints where appropriate

Example:
```python
def calculate_invoice_total(invoice_items: List[InvoiceItem]) -> float:
    """
    Calculate the total amount for an invoice.
    
    Args:
        invoice_items: List of invoice items
        
    Returns:
        Total amount as float
    """
    return sum(item.quantity * item.unit_price for item in invoice_items)
```

### JavaScript/React (Frontend)

- Follow ESLint configuration
- Use meaningful component and variable names
- Use functional components with hooks
- Keep components small and focused
- Add PropTypes for component props

Example:
```javascript
import PropTypes from 'prop-types';

const InvoiceItem = ({ item, onDelete }) => {
  const handleDelete = () => {
    onDelete(item.id);
  };

  return (
    <div className="invoice-item">
      <span>{item.description}</span>
      <span>${item.amount}</span>
      <button onClick={handleDelete}>Delete</button>
    </div>
  );
};

InvoiceItem.propTypes = {
  item: PropTypes.shape({
    id: PropTypes.number.isRequired,
    description: PropTypes.string.isRequired,
    amount: PropTypes.number.isRequired,
  }).isRequired,
  onDelete: PropTypes.func.isRequired,
};
```

## Testing

### Backend Testing

Create tests in a `tests/` directory:

```python
# tests/test_invoices.py
import unittest
from app import create_app
from extensions import db
from models.invoice import Invoice

class InvoiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_invoice(self):
        # Test invoice creation
        pass
```

Run tests:
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing

Create tests using React Testing Library:

```javascript
// src/components/__tests__/InvoiceItem.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import InvoiceItem from '../InvoiceItem';

describe('InvoiceItem', () => {
  const mockItem = {
    id: 1,
    description: 'Test Item',
    amount: 100,
  };

  const mockOnDelete = jest.fn();

  test('renders invoice item correctly', () => {
    render(<InvoiceItem item={mockItem} onDelete={mockOnDelete} />);
    
    expect(screen.getByText('Test Item')).toBeInTheDocument();
    expect(screen.getByText('$100')).toBeInTheDocument();
  });

  test('calls onDelete when delete button is clicked', () => {
    render(<InvoiceItem item={mockItem} onDelete={mockOnDelete} />);
    
    fireEvent.click(screen.getByText('Delete'));
    expect(mockOnDelete).toHaveBeenCalledWith(1);
  });
});
```

Run tests:
```bash
cd frontend
npm test
```

## Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation if needed

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new invoice template feature"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a pull request**:
   - Use a descriptive title
   - Provide a detailed description
   - Reference any related issues
   - Include screenshots for UI changes

### Commit Message Format

Use conventional commit format:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```
feat: add invoice template customization

- Add template selection dropdown
- Implement template preview
- Add template management API endpoints
- Update invoice creation form

Closes #123
```

## Bug Reports

When reporting bugs, please include:

1. **Clear description** of the bug
2. **Steps to reproduce** the issue
3. **Expected behavior** vs actual behavior
4. **Environment details**:
   - Operating system
   - Browser version (for frontend issues)
   - Python/Node.js versions
5. **Screenshots** if applicable
6. **Error messages** or logs

## Feature Requests

When requesting features, please:

1. **Describe the feature** clearly
2. **Explain the use case** and benefits
3. **Provide examples** of how it would work
4. **Consider implementation** complexity
5. **Check existing issues** to avoid duplicates

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Use welcoming and inclusive language
- Be collaborative and constructive
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Other conduct inappropriate in a professional setting

## Getting Help

- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check the README.md and inline code comments

## License

By contributing to SmoothBooks, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to SmoothBooks! 🚀
