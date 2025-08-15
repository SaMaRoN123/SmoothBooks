from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from extensions import db
from models.invoice import Invoice, Payment
from models.expense import Expense
from models.payroll import PayrollRecord, Employee
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_dashboard_overview():
    try:
        user_id = int(get_jwt_identity())
        print(f"Dashboard overview called for user_id: {user_id}")
        
        # Current month
        today = date.today()
        month_start = today.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Last month
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)
        last_month_end = month_start - timedelta(days=1)
        
        # Current month metrics
        current_month_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.user_id == user_id,
                Invoice.status == 'paid',
                Invoice.issue_date >= month_start,
                Invoice.issue_date <= month_end
            )
        ).scalar() or 0
        
        current_month_expenses = db.session.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.user_id == user_id,
                Expense.expense_date >= month_start,
                Expense.expense_date <= month_end
            )
        ).scalar() or 0
        
        current_month_payroll = db.session.query(func.sum(PayrollRecord.gross_pay)).join(Employee).filter(
            and_(
                Employee.user_id == user_id,
                PayrollRecord.pay_date >= month_start,
                PayrollRecord.pay_date <= month_end
            )
        ).scalar() or 0
        
        # Last month metrics for comparison
        last_month_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.user_id == user_id,
                Invoice.status == 'paid',
                Invoice.issue_date >= last_month_start,
                Invoice.issue_date <= last_month_end
            )
        ).scalar() or 0
        
        last_month_expenses = db.session.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.user_id == user_id,
                Expense.expense_date >= last_month_start,
                Expense.expense_date <= last_month_end
            )
        ).scalar() or 0
        
        # Calculate growth percentages
        revenue_growth = ((float(current_month_revenue) - float(last_month_revenue)) / float(last_month_revenue) * 100) if last_month_revenue > 0 else 0
        expense_growth = ((float(current_month_expenses) - float(last_month_expenses)) / float(last_month_expenses) * 100) if last_month_expenses > 0 else 0
        
        # Outstanding invoices
        outstanding_invoices = db.session.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.user_id == user_id,
                Invoice.status.in_(['sent', 'overdue'])
            )
        ).scalar() or 0
        
        # Recent activity
        recent_invoices = Invoice.query.filter_by(user_id=user_id).order_by(Invoice.created_at.desc()).limit(5).all()
        recent_expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.created_at.desc()).limit(5).all()
        
        return jsonify({
            'current_month': {
                'revenue': float(current_month_revenue),
                'expenses': float(current_month_expenses),
                'payroll': float(current_month_payroll),
                'profit': float(current_month_revenue) - float(current_month_expenses) - float(current_month_payroll)
            },
            'growth': {
                'revenue_growth': revenue_growth,
                'expense_growth': expense_growth
            },
            'outstanding_invoices': float(outstanding_invoices),
            'recent_activity': {
                'invoices': [invoice.to_dict() for invoice in recent_invoices],
                'expenses': [expense.to_dict() for expense in recent_expenses]
            }
        }), 200
    except Exception as e:
        print(f"Error in dashboard overview: {e}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/charts/revenue', methods=['GET'])
@jwt_required()
def get_revenue_chart():
    user_id = int(get_jwt_identity())
    months = request.args.get('months', 12, type=int)
    
    # Generate data for the last N months
    chart_data = []
    for i in range(months):
        month_start = date.today().replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.user_id == user_id,
                Invoice.status == 'paid',
                Invoice.issue_date >= month_start,
                Invoice.issue_date <= month_end
            )
        ).scalar() or 0
        
        chart_data.append({
            'month': month_start.strftime('%Y-%m'),
            'revenue': float(revenue)
        })
    
    # Reverse to show oldest first
    chart_data.reverse()
    
    return jsonify({'data': chart_data}), 200

@dashboard_bp.route('/charts/expenses', methods=['GET'])
@jwt_required()
def get_expenses_chart():
    user_id = int(get_jwt_identity())
    months = request.args.get('months', 12, type=int)
    
    # Generate data for the last N months
    chart_data = []
    for i in range(months):
        month_start = date.today().replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        expenses = db.session.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.user_id == user_id,
                Expense.expense_date >= month_start,
                Expense.expense_date <= month_end
            )
        ).scalar() or 0
        
        chart_data.append({
            'month': month_start.strftime('%Y-%m'),
            'expenses': float(expenses)
        })
    
    # Reverse to show oldest first
    chart_data.reverse()
    
    return jsonify({'data': chart_data}), 200

@dashboard_bp.route('/charts/expense-categories', methods=['GET'])
@jwt_required()
def get_expense_categories_chart():
    user_id = get_jwt_identity()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = (date.today() - timedelta(days=365)).isoformat()
    if not end_date:
        end_date = date.today().isoformat()
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get expenses by category
    category_data = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        and_(
            Expense.user_id == user_id,
            Expense.expense_date >= start_dt,
            Expense.expense_date <= end_dt
        )
    ).group_by(Expense.category).all()
    
    chart_data = [
        {'category': category, 'amount': float(total)}
        for category, total in category_data
    ]
    
    return jsonify({'data': chart_data}), 200

@dashboard_bp.route('/charts/invoice-status', methods=['GET'])
@jwt_required()
def get_invoice_status_chart():
    user_id = get_jwt_identity()
    
    # Get invoice counts by status
    status_data = db.session.query(
        Invoice.status,
        func.count(Invoice.id).label('count')
    ).filter_by(user_id=user_id).group_by(Invoice.status).all()
    
    chart_data = [
        {'status': status, 'count': count}
        for status, count in status_data
    ]
    
    return jsonify({'data': chart_data}), 200

@dashboard_bp.route('/quick-stats', methods=['GET'])
@jwt_required()
def get_quick_stats():
    user_id = get_jwt_identity()
    
    # Today's date
    today = date.today()
    
    # This month
    month_start = today.replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Quick stats
    total_invoices = Invoice.query.filter_by(user_id=user_id).count()
    paid_invoices = Invoice.query.filter_by(user_id=user_id, status='paid').count()
    overdue_invoices = Invoice.query.filter_by(user_id=user_id, status='overdue').count()
    
    total_expenses = Expense.query.filter_by(user_id=user_id).count()
    pending_expenses = Expense.query.filter_by(user_id=user_id, status='pending').count()
    
    total_employees = Employee.query.filter_by(user_id=user_id, status='active').count()
    
    # This month's totals
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
    
    return jsonify({
        'invoices': {
            'total': total_invoices,
            'paid': paid_invoices,
            'overdue': overdue_invoices,
            'payment_rate': (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0
        },
        'expenses': {
            'total': total_expenses,
            'pending': pending_expenses
        },
        'employees': {
            'active': total_employees
        },
        'this_month': {
            'revenue': float(month_revenue),
            'expenses': float(month_expenses),
            'profit': float(month_revenue) - float(month_expenses)
        }
    }), 200 