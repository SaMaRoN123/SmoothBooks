#!/usr/bin/env python3
"""
Seed script to populate the database with default expense categories
"""

from app import app
from extensions import db
from models.expense import ExpenseCategory

def seed_categories():
    """Seed the database with default expense categories"""
    
    default_categories = [
        {
            'name': 'office',
            'description': 'Office supplies and equipment',
            'color': '#1976d2'
        },
        {
            'name': 'travel',
            'description': 'Travel and transportation expenses',
            'color': '#388e3c'
        },
        {
            'name': 'meals',
            'description': 'Food and dining expenses',
            'color': '#f57c00'
        },
        {
            'name': 'utilities',
            'description': 'Utility bills and services',
            'color': '#7b1fa2'
        },
        {
            'name': 'marketing',
            'description': 'Marketing and advertising expenses',
            'color': '#d32f2f'
        },
        {
            'name': 'software',
            'description': 'Software licenses and subscriptions',
            'color': '#0288d1'
        },
        {
            'name': 'rent',
            'description': 'Office rent and lease payments',
            'color': '#8d6e63'
        },
        {
            'name': 'insurance',
            'description': 'Insurance premiums and coverage',
            'color': '#689f38'
        },
        {
            'name': 'other',
            'description': 'Other miscellaneous expenses',
            'color': '#757575'
        }
    ]
    
    with app.app_context():
        # Check if categories already exist
        existing_categories = ExpenseCategory.query.all()
        if existing_categories:
            print(f"Found {len(existing_categories)} existing categories:")
            for cat in existing_categories:
                print(f"  - {cat.name}")
            return
        
        # Create default categories
        for category_data in default_categories:
            category = ExpenseCategory(**category_data)
            db.session.add(category)
            print(f"Adding category: {category_data['name']}")
        
        try:
            db.session.commit()
            print(f"Successfully created {len(default_categories)} categories!")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating categories: {e}")

if __name__ == '__main__':
    seed_categories()
