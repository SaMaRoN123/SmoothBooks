from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
from dotenv import load_dotenv
from config import config
from extensions import db

# Load environment variables
load_dotenv()

jwt = JWTManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, 
         origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
         supports_credentials=True, 
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"Invalid token error: {error}")
        return jsonify({'error': 'Invalid token'}), 422
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"Missing token error: {error}")
        return jsonify({'error': 'Missing token'}), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"Expired token: {jwt_payload}")
        return jsonify({'error': 'Token has expired'}), 401
    
    # Import models to ensure they are registered with SQLAlchemy
    from models.user import User
    from models.invoice import Invoice, InvoiceItem, Payment
    from models.expense import Expense, ExpenseCategory
    from models.payroll import Employee, PayrollRecord, TimeEntry
    
    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.invoices import invoice_bp
    from routes.expenses import expense_bp
    from routes.payroll import payroll_bp
    from routes.reports import report_bp
    from routes.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(invoice_bp, url_prefix='/api/invoices')
    app.register_blueprint(expense_bp, url_prefix='/api/expenses')
    app.register_blueprint(payroll_bp, url_prefix='/api/payroll')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'SmoothBooks API is running'})
    
    # Favicon endpoint to prevent 404 errors
    @app.route('/favicon.ico')
    def favicon():
        return '', 204  # No content response
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000) 