from extensions import db
from datetime import datetime

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    hire_date = db.Column(db.Date, nullable=False)
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    salary = db.Column(db.Numeric(10, 2), nullable=False)
    hourly_rate = db.Column(db.Numeric(8, 2))
    tax_id = db.Column(db.String(20))  # SSN or equivalent
    status = db.Column(db.String(20), default='active')  # active, inactive, terminated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payroll_records = db.relationship('PayrollRecord', backref='employee', lazy=True)
    time_entries = db.relationship('TimeEntry', backref='employee', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'position': self.position,
            'department': self.department,
            'salary': float(self.salary),
            'hourly_rate': float(self.hourly_rate) if self.hourly_rate else None,
            'tax_id': self.tax_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PayrollRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    pay_date = db.Column(db.Date, nullable=False)
    regular_hours = db.Column(db.Numeric(8, 2), default=0.0)
    overtime_hours = db.Column(db.Numeric(8, 2), default=0.0)
    regular_pay = db.Column(db.Numeric(10, 2), default=0.0)
    overtime_pay = db.Column(db.Numeric(10, 2), default=0.0)
    gross_pay = db.Column(db.Numeric(10, 2), nullable=False)
    federal_tax = db.Column(db.Numeric(10, 2), default=0.0)
    state_tax = db.Column(db.Numeric(10, 2), default=0.0)
    social_security = db.Column(db.Numeric(10, 2), default=0.0)
    medicare = db.Column(db.Numeric(10, 2), default=0.0)
    other_deductions = db.Column(db.Numeric(10, 2), default=0.0)
    net_pay = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processed, paid
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'pay_period_start': self.pay_period_start.isoformat() if self.pay_period_start else None,
            'pay_period_end': self.pay_period_end.isoformat() if self.pay_period_end else None,
            'pay_date': self.pay_date.isoformat() if self.pay_date else None,
            'regular_hours': float(self.regular_hours),
            'overtime_hours': float(self.overtime_hours),
            'regular_pay': float(self.regular_pay),
            'overtime_pay': float(self.overtime_pay),
            'gross_pay': float(self.gross_pay),
            'federal_tax': float(self.federal_tax),
            'state_tax': float(self.state_tax),
            'social_security': float(self.social_security),
            'medicare': float(self.medicare),
            'other_deductions': float(self.other_deductions),
            'net_pay': float(self.net_pay),
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class TimeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    hours_worked = db.Column(db.Numeric(8, 2), nullable=False)
    is_overtime = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'hours_worked': float(self.hours_worked),
            'is_overtime': self.is_overtime,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        } 