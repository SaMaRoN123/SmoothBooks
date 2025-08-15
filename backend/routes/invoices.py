from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.invoice import Invoice, InvoiceItem, Payment
from models.user import User
from datetime import datetime, date
import uuid

invoice_bp = Blueprint('invoices', __name__)

@invoice_bp.route('', methods=['GET'])
@invoice_bp.route('/', methods=['GET'])
@jwt_required()
def get_invoices():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    query = Invoice.query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    invoices = query.order_by(Invoice.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'invoices': [invoice.to_dict() for invoice in invoices.items],
        'total': invoices.total,
        'pages': invoices.pages,
        'current_page': page
    }), 200

@invoice_bp.route('/<int:invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    user_id = get_jwt_identity()
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=user_id).first()
    
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    
    return jsonify({'invoice': invoice.to_dict()}), 200

@invoice_bp.route('', methods=['POST'])
@invoice_bp.route('/', methods=['POST'])
@jwt_required()
def create_invoice():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['client_name', 'issue_date', 'due_date', 'items']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Generate invoice number
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Calculate totals
    subtotal = sum(item['quantity'] * item['unit_price'] for item in data['items'])
    tax_rate = data.get('tax_rate', 0.0)
    tax_amount = subtotal * (tax_rate / 100)
    total_amount = subtotal + tax_amount
    
    # Create invoice
    invoice = Invoice(
        invoice_number=invoice_number,
        user_id=user_id,
        client_name=data['client_name'],
        client_email=data.get('client_email'),
        client_address=data.get('client_address'),
        issue_date=datetime.strptime(data['issue_date'], '%Y-%m-%d').date(),
        due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date(),
        subtotal=subtotal,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        total_amount=total_amount,
        status=data.get('status', 'draft'),
        notes=data.get('notes')
    )
    
    try:
        db.session.add(invoice)
        db.session.flush()  # Get invoice ID
        
        # Create invoice items
        for item_data in data['items']:
            item = InvoiceItem(
                invoice_id=invoice.id,
                description=item_data['description'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total=item_data['quantity'] * item_data['unit_price']
            )
            db.session.add(item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Invoice created successfully',
            'invoice': invoice.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Invoice creation failed'}), 500

@invoice_bp.route('/<int:invoice_id>', methods=['PUT'])
@jwt_required()
def update_invoice(invoice_id):
    user_id = get_jwt_identity()
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=user_id).first()
    
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    
    data = request.get_json()
    
    # Update invoice fields
    if data.get('client_name'):
        invoice.client_name = data['client_name']
    if data.get('client_email'):
        invoice.client_email = data['client_email']
    if data.get('client_address'):
        invoice.client_address = data['client_address']
    if data.get('issue_date'):
        invoice.issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d').date()
    if data.get('due_date'):
        invoice.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    if data.get('status'):
        invoice.status = data['status']
    if data.get('notes'):
        invoice.notes = data['notes']
    
    # Update items if provided
    if data.get('items'):
        # Delete existing items
        InvoiceItem.query.filter_by(invoice_id=invoice.id).delete()
        
        # Add new items
        subtotal = 0
        for item_data in data['items']:
            item = InvoiceItem(
                invoice_id=invoice.id,
                description=item_data['description'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total=item_data['quantity'] * item_data['unit_price']
            )
            db.session.add(item)
            subtotal += item.total
        
        # Recalculate totals
        invoice.subtotal = subtotal
        invoice.tax_amount = subtotal * (invoice.tax_rate / 100)
        invoice.total_amount = invoice.subtotal + invoice.tax_amount
    
    invoice.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Invoice updated successfully',
            'invoice': invoice.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Invoice update failed'}), 500

@invoice_bp.route('/<int:invoice_id>', methods=['DELETE'])
@jwt_required()
def delete_invoice(invoice_id):
    user_id = get_jwt_identity()
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=user_id).first()
    
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    
    try:
        db.session.delete(invoice)
        db.session.commit()
        return jsonify({'message': 'Invoice deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Invoice deletion failed'}), 500

@invoice_bp.route('/<int:invoice_id>/payments', methods=['POST'])
@jwt_required()
def add_payment(invoice_id):
    user_id = get_jwt_identity()
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=user_id).first()
    
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    
    data = request.get_json()
    
    if not data.get('amount') or not data.get('payment_date'):
        return jsonify({'error': 'Amount and payment date are required'}), 400
    
    payment = Payment(
        invoice_id=invoice_id,
        amount=data['amount'],
        payment_date=datetime.strptime(data['payment_date'], '%Y-%m-%d').date(),
        payment_method=data.get('payment_method'),
        reference_number=data.get('reference_number'),
        notes=data.get('notes')
    )
    
    try:
        db.session.add(payment)
        
        # Update invoice status if fully paid
        total_paid = sum(p.amount for p in invoice.payments) + float(data['amount'])
        if total_paid >= float(invoice.total_amount):
            invoice.status = 'paid'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment added successfully',
            'payment': payment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Payment addition failed'}), 500

@invoice_bp.route('/<int:invoice_id>/send', methods=['POST'])
@jwt_required()
def send_invoice(invoice_id):
    user_id = get_jwt_identity()
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=user_id).first()
    
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    
    if invoice.status != 'draft':
        return jsonify({'error': 'Only draft invoices can be sent'}), 400
    
    invoice.status = 'sent'
    invoice.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Invoice sent successfully',
            'invoice': invoice.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to send invoice'}), 500 