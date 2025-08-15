from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.invoice import Invoice, Payment
from models.expense import Expense
from models.payroll import PayrollRecord, Employee
from models.user import User
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_
import csv
import io
import json

report_bp = Blueprint('reports', __name__)

@report_bp.route('', methods=['GET'])
@report_bp.route('/', methods=['GET'])
@report_bp.route('/financial-summary', methods=['GET'])
@report_bp.route('/financial', methods=['GET'])
@jwt_required()
def get_financial_summary():
    user_id = get_jwt_identity()
    
    # Get date range from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = (date.today() - timedelta(days=365)).isoformat()
    if not end_date:
        end_date = date.today().isoformat()
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Debug logging
    print(f"Financial summary request for user {user_id}")
    print(f"Date range: {start_dt} to {end_dt}")
    
    # Total revenue (paid invoices)
    total_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
        and_(
            Invoice.user_id == user_id,
            Invoice.status == 'paid',
            Invoice.issue_date >= start_dt,
            Invoice.issue_date <= end_dt
        )
    ).scalar() or 0
    
    # Outstanding invoices
    outstanding_invoices = db.session.query(func.sum(Invoice.total_amount)).filter(
        and_(
            Invoice.user_id == user_id,
            Invoice.status.in_(['sent', 'overdue']),
            Invoice.issue_date >= start_dt,
            Invoice.issue_date <= end_dt
        )
    ).scalar() or 0
    
    # Total expenses
    total_expenses = db.session.query(func.sum(Expense.amount)).filter(
        and_(
            Expense.user_id == user_id,
            Expense.expense_date >= start_dt,
            Expense.expense_date <= end_dt
        )
    ).scalar() or 0
    
    # Payroll expenses
    payroll_expenses = db.session.query(func.sum(PayrollRecord.gross_pay)).join(Employee).filter(
        and_(
            Employee.user_id == user_id,
            PayrollRecord.pay_period_start >= start_dt,
            PayrollRecord.pay_period_start <= end_dt
        )
    ).scalar() or 0
    
    # Debug logging
    print(f"Total revenue: {total_revenue}")
    print(f"Outstanding invoices: {outstanding_invoices}")
    print(f"Total expenses: {total_expenses}")
    print(f"Payroll expenses: {payroll_expenses}")
    
    # Net profit
    net_profit = float(total_revenue) - float(total_expenses) - float(payroll_expenses)
    
    # Monthly breakdown
    monthly_data = []
    current_date = start_dt
    while current_date <= end_dt:
        month_start = current_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.user_id == user_id,
                Invoice.status == 'paid',
                Invoice.issue_date >= month_start,
                Invoice.issue_date <= month_end
            )
        ).scalar() or 0
        
        month_expenses = db.session.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.user_id == user_id,
                Expense.expense_date >= month_start,
                Expense.expense_date <= month_end
            )
        ).scalar() or 0
        
        monthly_data.append({
            'month': month_start.strftime('%Y-%m'),
            'revenue': float(month_revenue),
            'expenses': float(month_expenses),
            'profit': float(month_revenue) - float(month_expenses)
        })
        
        current_date = (month_start + timedelta(days=32)).replace(day=1)
    
    # Calculate profit margin
    profit_margin = (net_profit / float(total_revenue) * 100) if float(total_revenue) > 0 else 0
    
    # Get outstanding invoice count
    outstanding_count = db.session.query(func.count(Invoice.id)).filter(
        and_(
            Invoice.user_id == user_id,
            Invoice.status.in_(['sent', 'overdue']),
            Invoice.issue_date >= start_dt,
            Invoice.issue_date <= end_dt
        )
    ).scalar() or 0
    
    return jsonify({
        'period': {
            'start_date': start_date,
            'end_date': end_date
        },
        'total_revenue': float(total_revenue),
        'outstanding_amount': float(outstanding_invoices),
        'outstanding_count': outstanding_count,
        'total_expenses': float(total_expenses),
        'payroll_expenses': float(payroll_expenses),
        'net_profit': net_profit,
        'profit_margin': profit_margin,
        'revenue_growth': 0,  # Placeholder for future implementation
        'expense_growth': 0,  # Placeholder for future implementation
        'monthly_breakdown': monthly_data
    }), 200

@report_bp.route('/revenue', methods=['GET'])
@jwt_required()
def get_revenue_report():
    user_id = get_jwt_identity()
    range_param = request.args.get('range', 'month')
    
    # Calculate date range based on parameter
    end_date = date.today()
    if range_param == 'week':
        start_date = end_date - timedelta(days=7)
    elif range_param == 'month':
        start_date = end_date - timedelta(days=30)
    elif range_param == 'quarter':
        start_date = end_date - timedelta(days=90)
    elif range_param == 'year':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)
    
    # Get monthly revenue data
    monthly_data = []
    current_date = start_date
    while current_date <= end_date:
        month_start = current_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.user_id == user_id,
                Invoice.status == 'paid',
                Invoice.issue_date >= month_start,
                Invoice.issue_date <= month_end
            )
        ).scalar() or 0
        
        monthly_data.append({
            'month': month_start.strftime('%Y-%m'),
            'revenue': float(month_revenue)
        })
        
        current_date = (month_start + timedelta(days=32)).replace(day=1)
    
    return jsonify({
        'data': monthly_data
    }), 200

@report_bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_expenses_report():
    user_id = get_jwt_identity()
    range_param = request.args.get('range', 'month')
    
    # Calculate date range based on parameter
    end_date = date.today()
    if range_param == 'week':
        start_date = end_date - timedelta(days=7)
    elif range_param == 'month':
        start_date = end_date - timedelta(days=30)
    elif range_param == 'quarter':
        start_date = end_date - timedelta(days=90)
    elif range_param == 'year':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)
    
    # Get expense data by category
    expense_data = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('amount')
    ).filter(
        and_(
            Expense.user_id == user_id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        )
    ).group_by(Expense.category).all()
    
    chart_data = [
        {
            'name': category,
            'amount': float(amount)
        }
        for category, amount in expense_data
    ]
    
    return jsonify({
        'data': chart_data
    }), 200

@report_bp.route('/payroll', methods=['GET'])
@jwt_required()
def get_payroll_report():
    user_id = get_jwt_identity()
    range_param = request.args.get('range', 'month')
    
    # Calculate date range based on parameter
    end_date = date.today()
    if range_param == 'week':
        start_date = end_date - timedelta(days=7)
    elif range_param == 'month':
        start_date = end_date - timedelta(days=30)
    elif range_param == 'quarter':
        start_date = end_date - timedelta(days=90)
    elif range_param == 'year':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)
    
    # Get payroll data
    payroll_data = db.session.query(
        Employee.first_name,
        Employee.last_name,
        func.sum(PayrollRecord.gross_pay).label('total_pay'),
        func.count(PayrollRecord.id).label('pay_periods')
    ).join(PayrollRecord).filter(
        and_(
            Employee.user_id == user_id,
            PayrollRecord.pay_period_start >= start_date,
            PayrollRecord.pay_period_start <= end_date
        )
    ).group_by(Employee.id, Employee.first_name, Employee.last_name).all()
    
    payroll_summary = [
        {
            'employee_name': f"{first_name} {last_name}",
            'total_pay': float(total_pay),
            'pay_periods': pay_periods
        }
        for first_name, last_name, total_pay, pay_periods in payroll_data
    ]
    
    return jsonify({
        'payroll_data': payroll_summary
    }), 200

@report_bp.route('/tax-summary', methods=['GET'])
@jwt_required()
def get_tax_summary():
    user_id = get_jwt_identity()
    year = request.args.get('year', date.today().year)
    
    start_date = date(int(year), 1, 1)
    end_date = date(int(year), 12, 31)
    
    # Revenue for tax year
    total_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
        and_(
            Invoice.user_id == user_id,
            Invoice.status == 'paid',
            Invoice.issue_date >= start_date,
            Invoice.issue_date <= end_date
        )
    ).scalar() or 0
    
    # Business expenses
    business_expenses = db.session.query(func.sum(Expense.amount)).filter(
        and_(
            Expense.user_id == user_id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        )
    ).scalar() or 0
    
    # Payroll expenses
    payroll_expenses = db.session.query(func.sum(PayrollRecord.gross_pay)).join(Employee).filter(
        and_(
            Employee.user_id == user_id,
            PayrollRecord.pay_period_start >= start_date,
            PayrollRecord.pay_period_start <= end_date
        )
    ).scalar() or 0
    
    # Tax calculations (simplified)
    gross_income = float(total_revenue)
    total_expenses = float(business_expenses) + float(payroll_expenses)
    net_income = gross_income - total_expenses
    
    # Estimated taxes (simplified calculation)
    estimated_tax = net_income * 0.25  # 25% estimated tax rate
    
    return jsonify({
        'tax_year': year,
        'income': {
            'gross_revenue': gross_income,
            'total_expenses': total_expenses,
            'net_income': net_income
        },
        'expenses_breakdown': {
            'business_expenses': float(business_expenses),
            'payroll_expenses': float(payroll_expenses)
        },
        'tax_estimate': {
            'estimated_tax': estimated_tax,
            'effective_tax_rate': (estimated_tax / gross_income * 100) if gross_income > 0 else 0
        }
    }), 200

@report_bp.route('/invoice-report', methods=['GET'])
@jwt_required()
def get_invoice_report():
    user_id = get_jwt_identity()
    range_param = request.args.get('range', 'month')
    status = request.args.get('status')
    
    # Calculate date range based on parameter
    end_date = date.today()
    if range_param == 'week':
        start_date = end_date - timedelta(days=7)
    elif range_param == 'month':
        start_date = end_date - timedelta(days=30)
    elif range_param == 'quarter':
        start_date = end_date - timedelta(days=90)
    elif range_param == 'year':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)
    
    query = Invoice.query.filter_by(user_id=user_id)
    
    # Apply date range filter
    query = query.filter(Invoice.issue_date >= start_date)
    query = query.filter(Invoice.issue_date <= end_date)
    
    if status:
        query = query.filter(Invoice.status == status)
    
    invoices = query.order_by(Invoice.issue_date.desc()).all()
    
    # Calculate summary
    total_invoiced = sum(invoice.total_amount for invoice in invoices)
    total_paid = sum(invoice.total_amount for invoice in invoices if invoice.status == 'paid')
    total_outstanding = sum(invoice.total_amount for invoice in invoices if invoice.status in ['sent', 'overdue'])
    
    # Group by status
    status_summary = {}
    for invoice in invoices:
        status = invoice.status
        if status not in status_summary:
            status_summary[status] = {'count': 0, 'total': 0}
        status_summary[status]['count'] += 1
        status_summary[status]['total'] += float(invoice.total_amount)
    
    return jsonify({
        'invoices': [invoice.to_dict() for invoice in invoices],
        'summary': {
            'total_invoiced': float(total_invoiced),
            'total_paid': float(total_paid),
            'total_outstanding': float(total_outstanding),
            'payment_rate': (float(total_paid) / float(total_invoiced) * 100) if total_invoiced > 0 else 0
        },
        'status_breakdown': status_summary
    }), 200

@report_bp.route('/expense-report', methods=['GET'])
@jwt_required()
def get_expense_report():
    user_id = get_jwt_identity()
    range_param = request.args.get('range', 'month')
    category = request.args.get('category')
    
    # Calculate date range based on parameter
    end_date = date.today()
    if range_param == 'week':
        start_date = end_date - timedelta(days=7)
    elif range_param == 'month':
        start_date = end_date - timedelta(days=30)
    elif range_param == 'quarter':
        start_date = end_date - timedelta(days=90)
    elif range_param == 'year':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)
    
    query = Expense.query.filter_by(user_id=user_id)
    
    # Apply date range filter
    query = query.filter(Expense.expense_date >= start_date)
    query = query.filter(Expense.expense_date <= end_date)
    
    if category:
        query = query.filter(Expense.category == category)
    
    expenses = query.order_by(Expense.expense_date.desc()).all()
    
    # Calculate summary
    total_expenses = sum(expense.amount for expense in expenses)
    
    # Group by category
    category_summary = {}
    for expense in expenses:
        category = expense.category
        if category not in category_summary:
            category_summary[category] = {'count': 0, 'total': 0}
        category_summary[category]['count'] += 1
        category_summary[category]['total'] += float(expense.amount)
    
    return jsonify({
        'expenses': [expense.to_dict() for expense in expenses],
        'summary': {
            'total_expenses': float(total_expenses),
            'expense_count': len(expenses)
        },
        'category_breakdown': category_summary
    }), 200

@report_bp.route('/export/csv', methods=['GET'])
@jwt_required()
def export_csv():
    user_id = get_jwt_identity()
    report_type = request.args.get('type', 'invoices')
    range_param = request.args.get('range', 'month')
    
    # Calculate date range based on parameter
    end_date = date.today()
    if range_param == 'week':
        start_date = end_date - timedelta(days=7)
    elif range_param == 'month':
        start_date = end_date - timedelta(days=30)
    elif range_param == 'quarter':
        start_date = end_date - timedelta(days=90)
    elif range_param == 'year':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)
    
    start_dt = start_date
    end_dt = end_date
    
    # Create CSV data
    output = io.StringIO()
    writer = csv.writer(output)
    
    if report_type == 'invoices':
        writer.writerow(['Invoice Number', 'Client', 'Issue Date', 'Due Date', 'Amount', 'Status'])
        
        invoices = Invoice.query.filter(
            and_(
                Invoice.user_id == user_id,
                Invoice.issue_date >= start_dt,
                Invoice.issue_date <= end_dt
            )
        ).all()
        
        for invoice in invoices:
            writer.writerow([
                invoice.invoice_number,
                invoice.client_name,
                invoice.issue_date.isoformat(),
                invoice.due_date.isoformat(),
                invoice.total_amount,
                invoice.status
            ])
    
    elif report_type == 'expenses':
        writer.writerow(['Date', 'Category', 'Description', 'Amount', 'Vendor', 'Status'])
        
        expenses = Expense.query.filter(
            and_(
                Expense.user_id == user_id,
                Expense.expense_date >= start_dt,
                Expense.expense_date <= end_dt
            )
        ).all()
        
        for expense in expenses:
            writer.writerow([
                expense.expense_date.isoformat(),
                expense.category,
                expense.description,
                expense.amount,
                expense.vendor or '',
                expense.status
            ])
    
    elif report_type == 'payroll':
        writer.writerow(['Employee', 'Pay Period', 'Gross Pay', 'Net Pay', 'Status'])
        
        records = PayrollRecord.query.join(Employee).filter(
            and_(
                Employee.user_id == user_id,
                PayrollRecord.pay_period_start >= start_dt,
                PayrollRecord.pay_period_start <= end_dt
            )
        ).all()
        
        for record in records:
            writer.writerow([
                f"{record.employee.first_name} {record.employee.last_name}",
                f"{record.pay_period_start.isoformat()} - {record.pay_period_end.isoformat()}",
                record.gross_pay,
                record.net_pay,
                record.status
            ])
    
    # Create response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{report_type}_report_{start_date}_to_{end_date}.csv'
    )

@report_bp.route('/export/json', methods=['GET'])
@jwt_required()
def export_json():
    user_id = get_jwt_identity()
    report_type = request.args.get('type', 'financial_summary')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = date.today().isoformat()
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    data = {}
    
    if report_type == 'financial_summary':
        # Get financial summary data
        total_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.user_id == user_id,
                Invoice.status == 'paid',
                Invoice.issue_date >= start_dt,
                Invoice.issue_date <= end_dt
            )
        ).scalar() or 0
        
        total_expenses = db.session.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.user_id == user_id,
                Expense.expense_date >= start_dt,
                Expense.expense_date <= end_dt
            )
        ).scalar() or 0
        
        data = {
            'report_type': 'financial_summary',
            'period': {'start_date': start_date, 'end_date': end_date},
            'summary': {
                'total_revenue': float(total_revenue),
                'total_expenses': float(total_expenses),
                'net_profit': float(total_revenue) - float(total_expenses)
            }
        }
    
    # Create response
    return send_file(
        io.BytesIO(json.dumps(data, indent=2).encode('utf-8')),
        mimetype='application/json',
        as_attachment=True,
        download_name=f'{report_type}_report_{start_date}_to_{end_date}.json'
    ) 