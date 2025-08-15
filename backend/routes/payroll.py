from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.payroll import Employee, PayrollRecord, TimeEntry
from datetime import datetime, date, timedelta
from sqlalchemy import func
import uuid

payroll_bp = Blueprint('payroll', __name__)

# Employee routes
@payroll_bp.route('/employees', methods=['GET'])
@jwt_required()
def get_employees():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    query = Employee.query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    employees = query.order_by(Employee.last_name).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'employees': [employee.to_dict() for employee in employees.items],
        'total': employees.total,
        'pages': employees.pages,
        'current_page': page
    }), 200

@payroll_bp.route('/employees/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    user_id = get_jwt_identity()
    employee = Employee.query.filter_by(id=employee_id, user_id=user_id).first()
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    return jsonify({'employee': employee.to_dict()}), 200

@payroll_bp.route('/employees', methods=['POST'])
@jwt_required()
def create_employee():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Debug logging
    print(f"Creating employee with data: {data}")
    
    # Validate required fields
    required_fields = ['first_name', 'last_name', 'email', 'hire_date', 'salary']
    for field in required_fields:
        if not data.get(field):
            print(f"Missing required field: {field}")
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if email already exists
    if Employee.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email address already exists'}), 400
    
    # Generate employee ID
    employee_id = f"EMP-{str(uuid.uuid4())[:8].upper()}"
    
    # Convert salary to float for database storage
    try:
        salary = float(data['salary'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid salary value'}), 400
    
    # Convert hourly_rate to float if provided
    hourly_rate = None
    if data.get('hourly_rate'):
        try:
            hourly_rate = float(data['hourly_rate'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid hourly rate value'}), 400
    
    employee = Employee(
        user_id=user_id,
        employee_id=employee_id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data.get('phone'),
        address=data.get('address'),
        hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date(),
        position=data.get('position'),
        department=data.get('department'),
        salary=salary,
        hourly_rate=hourly_rate,
        tax_id=data.get('tax_id'),
        status=data.get('status', 'active')
    )
    
    try:
        db.session.add(employee)
        db.session.commit()
        
        return jsonify({
            'message': 'Employee created successfully',
            'employee': employee.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Employee creation error: {str(e)}")
        # Check for specific database errors
        if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
            if "email" in str(e):
                return jsonify({'error': 'Email address already exists'}), 400
            elif "employee_id" in str(e):
                return jsonify({'error': 'Employee ID already exists'}), 400
        return jsonify({'error': f'Employee creation failed: {str(e)}'}), 500

@payroll_bp.route('/employees/<int:employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    user_id = get_jwt_identity()
    employee = Employee.query.filter_by(id=employee_id, user_id=user_id).first()
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    data = request.get_json()
    
    # Update employee fields
    if data.get('first_name'):
        employee.first_name = data['first_name']
    if data.get('last_name'):
        employee.last_name = data['last_name']
    if data.get('email'):
        employee.email = data['email']
    if data.get('phone'):
        employee.phone = data['phone']
    if data.get('address'):
        employee.address = data['address']
    if data.get('position'):
        employee.position = data['position']
    if data.get('department'):
        employee.department = data['department']
    if data.get('salary'):
        employee.salary = data['salary']
    if data.get('hourly_rate'):
        employee.hourly_rate = data['hourly_rate']
    if data.get('tax_id'):
        employee.tax_id = data['tax_id']
    if data.get('status'):
        employee.status = data['status']
    
    employee.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Employee updated successfully',
            'employee': employee.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Employee update failed'}), 500

@payroll_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(employee_id):
    user_id = get_jwt_identity()
    employee = Employee.query.filter_by(id=employee_id, user_id=user_id).first()
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    try:
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'message': 'Employee deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Employee deletion failed'}), 500

# Payroll routes
@payroll_bp.route('', methods=['GET'])
@payroll_bp.route('/', methods=['GET'])
@payroll_bp.route('/payroll', methods=['GET'])
@payroll_bp.route('/records', methods=['GET'])
@jwt_required()
def get_payroll_records():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    employee_id = request.args.get('employee_id')
    status = request.args.get('status')
    
    query = PayrollRecord.query.join(Employee).filter(Employee.user_id == user_id)
    
    if employee_id:
        query = query.filter(PayrollRecord.employee_id == employee_id)
    
    if status:
        query = query.filter(PayrollRecord.status == status)
    
    records = query.order_by(PayrollRecord.pay_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'payroll_records': [record.to_dict() for record in records.items],
        'total': records.total,
        'pages': records.pages,
        'current_page': page
    }), 200

@payroll_bp.route('/payroll/<int:record_id>', methods=['GET'])
@jwt_required()
def get_payroll_record(record_id):
    user_id = get_jwt_identity()
    record = PayrollRecord.query.join(Employee).filter(
        PayrollRecord.id == record_id,
        Employee.user_id == user_id
    ).first()
    
    if not record:
        return jsonify({'error': 'Payroll record not found'}), 404
    
    return jsonify({'payroll_record': record.to_dict()}), 200

@payroll_bp.route('/payroll', methods=['POST'])
@jwt_required()
def create_payroll_record():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['employee_id', 'pay_period_start', 'pay_period_end', 'pay_date']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Verify employee belongs to user
    employee = Employee.query.filter_by(id=data['employee_id'], user_id=user_id).first()
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    # Calculate payroll
    regular_hours = data.get('regular_hours', 0)
    overtime_hours = data.get('overtime_hours', 0)
    
    if employee.hourly_rate:
        regular_pay = regular_hours * float(employee.hourly_rate)
        overtime_pay = overtime_hours * float(employee.hourly_rate) * 1.5
    else:
        # Salary-based calculation
        regular_pay = float(employee.salary) / 26  # Bi-weekly
        overtime_pay = 0
    
    gross_pay = regular_pay + overtime_pay
    
    # Calculate taxes (simplified)
    federal_tax = gross_pay * 0.15
    state_tax = gross_pay * 0.05
    social_security = gross_pay * 0.062
    medicare = gross_pay * 0.0145
    other_deductions = data.get('other_deductions', 0)
    
    net_pay = gross_pay - federal_tax - state_tax - social_security - medicare - other_deductions
    
    record = PayrollRecord(
        employee_id=data['employee_id'],
        pay_period_start=datetime.strptime(data['pay_period_start'], '%Y-%m-%d').date(),
        pay_period_end=datetime.strptime(data['pay_period_end'], '%Y-%m-%d').date(),
        pay_date=datetime.strptime(data['pay_date'], '%Y-%m-%d').date(),
        regular_hours=regular_hours,
        overtime_hours=overtime_hours,
        regular_pay=regular_pay,
        overtime_pay=overtime_pay,
        gross_pay=gross_pay,
        federal_tax=federal_tax,
        state_tax=state_tax,
        social_security=social_security,
        medicare=medicare,
        other_deductions=other_deductions,
        net_pay=net_pay,
        status=data.get('status', 'pending'),
        notes=data.get('notes')
    )
    
    try:
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'message': 'Payroll record created successfully',
            'payroll_record': record.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Payroll record creation failed'}), 500

# Time tracking routes
@payroll_bp.route('/time-entries', methods=['GET'])
@jwt_required()
def get_time_entries():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    employee_id = request.args.get('employee_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = TimeEntry.query.join(Employee).filter(Employee.user_id == user_id)
    
    if employee_id:
        query = query.filter(TimeEntry.employee_id == employee_id)
    
    if start_date:
        query = query.filter(TimeEntry.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    if end_date:
        query = query.filter(TimeEntry.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    entries = query.order_by(TimeEntry.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'time_entries': [entry.to_dict() for entry in entries.items],
        'total': entries.total,
        'pages': entries.pages,
        'current_page': page
    }), 200

@payroll_bp.route('/time-entries', methods=['POST'])
@jwt_required()
def create_time_entry():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['employee_id', 'date', 'start_time', 'end_time']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Verify employee belongs to user
    employee = Employee.query.filter_by(id=data['employee_id'], user_id=user_id).first()
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    # Calculate hours worked
    start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    end_time = datetime.strptime(data['end_time'], '%H:%M').time()
    
    start_dt = datetime.combine(datetime.strptime(data['date'], '%Y-%m-%d').date(), start_time)
    end_dt = datetime.combine(datetime.strptime(data['date'], '%Y-%m-%d').date(), end_time)
    
    hours_worked = (end_dt - start_dt).total_seconds() / 3600
    is_overtime = hours_worked > 8
    
    entry = TimeEntry(
        employee_id=data['employee_id'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        start_time=start_time,
        end_time=end_time,
        hours_worked=hours_worked,
        is_overtime=is_overtime,
        notes=data.get('notes')
    )
    
    try:
        db.session.add(entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Time entry created successfully',
            'time_entry': entry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Time entry creation failed'}), 500

@payroll_bp.route('/process', methods=['POST'])
@jwt_required()
def process_payroll():
    user_id = get_jwt_identity()
    
    try:
        # Get all active employees
        employees = Employee.query.filter_by(user_id=user_id, status='active').all()
        
        # Get time entries for the current pay period (last 2 weeks)
        end_date = date.today()
        start_date = end_date - timedelta(days=14)
        
        time_entries = TimeEntry.query.join(Employee).filter(
            Employee.user_id == user_id,
            TimeEntry.date >= start_date,
            TimeEntry.date <= end_date
        ).all()
        
        # Group time entries by employee
        employee_hours = {}
        for entry in time_entries:
            if entry.employee_id not in employee_hours:
                employee_hours[entry.employee_id] = 0
            employee_hours[entry.employee_id] += entry.hours_worked
        
        # Create payroll records for each employee
        created_records = []
        for employee in employees:
            total_hours = employee_hours.get(employee.id, 0)
            
            if total_hours > 0:
                # Calculate pay based on hourly rate or salary
                if employee.hourly_rate:
                    gross_pay = total_hours * employee.hourly_rate
                else:
                    # Assume salary is monthly, calculate pro-rated amount
                    gross_pay = (employee.salary / 30) * 14  # 2 weeks
                
                # Simple tax calculation (15% for demo)
                tax_amount = gross_pay * 0.15
                net_pay = gross_pay - tax_amount
                
                # Check if payroll record already exists for this period
                existing_record = PayrollRecord.query.filter_by(
                    employee_id=employee.id,
                    pay_period_start=start_date,
                    pay_period_end=end_date
                ).first()
                
                if not existing_record:
                    record = PayrollRecord(
                        employee_id=employee.id,
                        pay_period_start=start_date,
                        pay_period_end=end_date,
                        pay_date=end_date,
                        regular_hours=min(total_hours, 80),  # 80 hours for 2 weeks
                        overtime_hours=max(0, total_hours - 80),
                        regular_pay=min(total_hours, 80) * (employee.hourly_rate or (employee.salary / 160)),
                        overtime_pay=max(0, total_hours - 80) * (employee.hourly_rate or (employee.salary / 160)) * 1.5,
                        gross_pay=gross_pay,
                        federal_tax=tax_amount * 0.6,  # 60% of total tax
                        state_tax=tax_amount * 0.2,   # 20% of total tax
                        social_security=tax_amount * 0.15,  # 15% of total tax
                        medicare=tax_amount * 0.05,   # 5% of total tax
                        net_pay=net_pay,
                        status='pending'
                    )
                    db.session.add(record)
                    created_records.append(record)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Payroll processed successfully. Created {len(created_records)} records.',
            'records_created': len(created_records)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Payroll processing failed'}), 500