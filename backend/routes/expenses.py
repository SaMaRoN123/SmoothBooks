from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.expense import Expense, ExpenseCategory
from datetime import datetime, date, timedelta
from sqlalchemy import func

expense_bp = Blueprint('expenses', __name__)

@expense_bp.route('', methods=['GET'])
@expense_bp.route('/', methods=['GET'])
@jwt_required()
def get_expenses():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Expense.query.filter_by(user_id=user_id)
    
    if category:
        query = query.filter_by(category=category)
    
    if start_date:
        query = query.filter(Expense.expense_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    if end_date:
        query = query.filter(Expense.expense_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    expenses = query.order_by(Expense.expense_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'expenses': [expense.to_dict() for expense in expenses.items],
        'total': expenses.total,
        'pages': expenses.pages,
        'current_page': page
    }), 200

@expense_bp.route('/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    
    return jsonify({'expense': expense.to_dict()}), 200

@expense_bp.route('', methods=['POST'])
@expense_bp.route('/', methods=['POST'])
@jwt_required()
def create_expense():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['category', 'description', 'amount', 'expense_date']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    expense = Expense(
        user_id=user_id,
        category=data['category'],
        description=data['description'],
        amount=data['amount'],
        expense_date=datetime.strptime(data['expense_date'], '%Y-%m-%d').date(),
        vendor=data.get('vendor'),
        receipt_url=data.get('receipt_url'),
        payment_method=data.get('payment_method'),
        status=data.get('status', 'pending'),
        notes=data.get('notes')
    )
    
    try:
        db.session.add(expense)
        db.session.commit()
        
        return jsonify({
            'message': 'Expense created successfully',
            'expense': expense.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Expense creation failed'}), 500

@expense_bp.route('/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    
    data = request.get_json()
    
    # Update expense fields
    if data.get('category'):
        expense.category = data['category']
    if data.get('description'):
        expense.description = data['description']
    if data.get('amount'):
        expense.amount = data['amount']
    if data.get('expense_date'):
        expense.expense_date = datetime.strptime(data['expense_date'], '%Y-%m-%d').date()
    if data.get('vendor'):
        expense.vendor = data['vendor']
    if data.get('receipt_url'):
        expense.receipt_url = data['receipt_url']
    if data.get('payment_method'):
        expense.payment_method = data['payment_method']
    if data.get('status'):
        expense.status = data['status']
    if data.get('notes'):
        expense.notes = data['notes']
    
    expense.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Expense updated successfully',
            'expense': expense.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Expense update failed'}), 500

@expense_bp.route('/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    
    try:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'message': 'Expense deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Expense deletion failed'}), 500

@expense_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    categories = ExpenseCategory.query.all()
    return jsonify({'categories': [category.to_dict() for category in categories]}), 200

@expense_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Category name is required'}), 400
    
    # Check if category already exists
    if ExpenseCategory.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Category already exists'}), 400
    
    category = ExpenseCategory(
        name=data['name'],
        description=data.get('description'),
        color=data.get('color', '#000000')
    )
    
    try:
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category created successfully',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Category creation failed'}), 500

@expense_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_expense_summary():
    user_id = get_jwt_identity()
    
    # Get date range from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Expense.query.filter_by(user_id=user_id)
    
    if start_date:
        query = query.filter(Expense.expense_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    if end_date:
        query = query.filter(Expense.expense_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    # Total expenses
    total_expenses = query.with_entities(func.sum(Expense.amount)).scalar() or 0
    
    # Expenses by category
    category_summary = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter_by(user_id=user_id).group_by(Expense.category).all()
    
    # Monthly expenses (last 12 months)
    monthly_expenses = []
    for i in range(12):
        month_start = date.today().replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        month_total = Expense.query.filter(
            Expense.user_id == user_id,
            Expense.expense_date >= month_start,
            Expense.expense_date <= month_end
        ).with_entities(func.sum(Expense.amount)).scalar() or 0
        
        monthly_expenses.append({
            'month': month_start.strftime('%Y-%m'),
            'total': float(month_total)
        })
    
    return jsonify({
        'total_expenses': float(total_expenses),
        'category_summary': [
            {'category': cat, 'total': float(total)} 
            for cat, total in category_summary
        ],
        'monthly_expenses': monthly_expenses
    }), 200 