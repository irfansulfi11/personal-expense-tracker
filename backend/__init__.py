from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy globally
db = SQLAlchemy()

# ✅ App factory function
def create_app():
    app = Flask(__name__)

    # Configuration
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "expenses.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000", "methods": ["GET", "POST", "PUT", "DELETE"]}})

    # ✅ Health check route
    @app.route('/')
    def index():
        return {'message': 'Expense Tracker API is running'}

    # ✅ Register Blueprints
    try:
        from api.routes import expense_bp
        app.register_blueprint(expense_bp)
        logger.info("Expense blueprint registered successfully")
    except Exception as e:
        logger.error(f"Failed to register expense blueprint: {str(e)}")
        raise

    # ✅ Create tables and seed data
    with app.app_context():
        # Import models here to ensure they're registered before creating tables
        from api.models.expense import Expense
        from api.models.income import Income  # Import Income model
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}")
            raise

        # Seed data if the table is empty
        try:
            if not Expense.query.first():
                expenses = [
                    Expense(category='Food', amount=50.0, description='Grocery shopping', date=datetime.strptime('2025-06-01', '%Y-%m-%d').date()),
                    Expense(category='Transport', amount=30.0, description='Bus fare', date=datetime.strptime('2025-06-02', '%Y-%m-%d').date()),
                    Expense(category='Entertainment', amount=120.0, description='Movie tickets', date=datetime.strptime('2025-06-03', '%Y-%m-%d').date()),
                    Expense(category='Food', amount=25.0, description='Lunch', date=datetime.strptime('2025-06-04', '%Y-%m-%d').date()),
                    Expense(category='Utilities', amount=80.0, description='Electricity bill', date=datetime.strptime('2025-06-05', '%Y-%m-%d').date()),
                    Expense(category='Shopping', amount=200.0, description='Clothes', date=datetime.strptime('2025-06-06', '%Y-%m-%d').date()),
                    Expense(category='Food', amount=45.0, description='Dinner out', date=datetime.strptime('2025-06-07', '%Y-%m-%d').date()),
                    Expense(category='Transport', amount=15.0, description='Uber ride', date=datetime.strptime('2025-06-08', '%Y-%m-%d').date()),
                    Expense(category='Healthcare', amount=150.0, description='Doctor visit', date=datetime.strptime('2025-06-09', '%Y-%m-%d').date()),
                    Expense(category='Entertainment', amount=60.0, description='Concert tickets', date=datetime.strptime('2025-06-10', '%Y-%m-%d').date()),
                ]
                db.session.bulk_save_objects(expenses)
                db.session.commit()
                logger.info("Database seeded with initial expenses")
            else:
                logger.info("Database already contains data, skipping seeding")

            # Seed income data if table is empty
            if not Income.query.first():
                incomes = [
                    Income(source='Salary', amount=5000.0, description='Monthly salary', date=datetime.strptime('2025-06-01', '%Y-%m-%d').date(), is_recurring=True),
                    Income(source='Freelance', amount=1500.0, description='Web development project', date=datetime.strptime('2025-06-05', '%Y-%m-%d').date(), is_recurring=False),
                    Income(source='Investment', amount=200.0, description='Dividend from stocks', date=datetime.strptime('2025-06-10', '%Y-%m-%d').date(), is_recurring=False),
                ]
                db.session.bulk_save_objects(incomes)
                db.session.commit()
                logger.info("Database seeded with initial income data")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to seed database: {str(e)}")
            raise

    return app