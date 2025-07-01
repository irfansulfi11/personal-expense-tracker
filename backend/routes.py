from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from api import db
from api.models.expense import Expense
from api.models.income import Income  # Fixed import

# Blueprint setup
expense_bp = Blueprint('expense_routes', __name__, url_prefix='/api')

# ===== EXPENSE ROUTES =====
@expense_bp.route('/expenses', methods=['GET'])
def get_expenses():
    try:
        expenses = Expense.query.order_by(Expense.date.desc()).all()
        return jsonify([expense.to_dict() for expense in expenses])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/expenses', methods=['POST'])
def create_expense():
    try:
        data = request.get_json()
        if not data.get('category') or not data.get('amount'):
            return jsonify({'error': 'Category and amount are required'}), 400

        expense_date = datetime.utcnow().date()
        if data.get('date'):
            try:
                expense_date = datetime.fromisoformat(data['date']).date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        expense = Expense(
            category=data['category'],
            amount=float(data['amount']),
            description=data.get('description', ''),
            date=expense_date
        )

        db.session.add(expense)
        db.session.commit()
        return jsonify(expense.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    try:
        expense = Expense.query.get_or_404(expense_id)
        return jsonify(expense.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    try:
        expense = Expense.query.get_or_404(expense_id)
        data = request.get_json()

        if data.get('category'):
            expense.category = data['category']
        if data.get('amount'):
            expense.amount = float(data['amount'])
        if 'description' in data:
            expense.description = data['description']
        if data.get('date'):
            try:
                expense.date = datetime.fromisoformat(data['date']).date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        db.session.commit()
        return jsonify(expense.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        expense = Expense.query.get_or_404(expense_id)
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'message': 'Expense deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== INCOME ROUTES =====
@expense_bp.route('/incomes', methods=['GET'])
def get_incomes():
    try:
        incomes = Income.query.order_by(Income.date.desc()).all()
        return jsonify([income.to_dict() for income in incomes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/incomes', methods=['POST'])
def create_income():
    try:
        data = request.get_json()
        if not data.get('source') or not data.get('amount'):
            return jsonify({'error': 'Source and amount are required'}), 400

        income_date = datetime.utcnow().date()
        if data.get('date'):
            try:
                income_date = datetime.fromisoformat(data['date']).date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        income = Income(
            source=data['source'],
            amount=float(data['amount']),
            description=data.get('description', ''),
            date=income_date,
            is_recurring=data.get('is_recurring', False)
        )

        db.session.add(income)
        db.session.commit()
        return jsonify(income.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/incomes/<int:income_id>', methods=['GET'])
def get_income(income_id):
    try:
        income = Income.query.get_or_404(income_id)
        return jsonify(income.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/incomes/<int:income_id>', methods=['PUT'])
def update_income(income_id):
    try:
        income = Income.query.get_or_404(income_id)
        data = request.get_json()

        if data.get('source'):
            income.source = data['source']
        if data.get('amount'):
            income.amount = float(data['amount'])
        if 'description' in data:
            income.description = data['description']
        if 'is_recurring' in data:
            income.is_recurring = data['is_recurring']
        if data.get('date'):
            try:
                income.date = datetime.fromisoformat(data['date']).date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        db.session.commit()
        return jsonify(income.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/incomes/<int:income_id>', methods=['DELETE'])
def delete_income(income_id):
    try:
        income = Income.query.get_or_404(income_id)
        db.session.delete(income)
        db.session.commit()
        return jsonify({'message': 'Income deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== AI-POWERED INSIGHTS =====
def generate_ai_insights(expenses, incomes):
    """Generate AI-powered financial insights and recommendations"""
    insights = {
        'financial_health': {},
        'spending_patterns': {},
        'ai_recommendations': [],
        'behavioral_insights': [],
        'future_predictions': {}
    }
    
    if not expenses and not incomes:
        return insights
    
    # Calculate basic metrics
    total_expenses = sum(exp.amount for exp in expenses)
    total_income = sum(inc.amount for inc in incomes)
    net_savings = total_income - total_expenses
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
    
    # Financial Health Analysis
    insights['financial_health'] = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_savings': net_savings,
        'savings_rate': savings_rate,
        'financial_score': min(100, max(0, savings_rate + 50))  # Score out of 100
    }
    
    # Spending Pattern Analysis
    category_breakdown = defaultdict(float)
    monthly_trends = defaultdict(float)
    
    for expense in expenses:
        category_breakdown[expense.category] += expense.amount
        month_key = f"{expense.date.year}-{expense.date.month:02d}"
        monthly_trends[month_key] += expense.amount
    
    insights['spending_patterns'] = {
        'category_breakdown': dict(category_breakdown),
        'monthly_trends': dict(monthly_trends),
        'top_categories': sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)[:3]
    }
    
    # AI Recommendations based on patterns
    recommendations = []
    
    # Savings rate recommendations
    if savings_rate < 10:
        recommendations.append({
            'title': 'Emergency: Low Savings Rate',
            'message': f'Your savings rate is {savings_rate:.1f}%. Aim for at least 20%. Consider cutting non-essential expenses immediately.',
            'priority': 'critical',
            'action': 'Reduce discretionary spending by 30%',
            'potential_savings': total_expenses * 0.3
        })
    elif savings_rate < 20:
        recommendations.append({
            'title': 'Improve Savings Rate',
            'message': f'Your savings rate is {savings_rate:.1f}%. Try to reach 20% for better financial security.',
            'priority': 'high',
            'action': 'Identify and reduce top 2 expense categories',
            'potential_savings': total_expenses * 0.1
        })
    else:
        recommendations.append({
            'title': 'Excellent Savings!',
            'message': f'Great work! Your savings rate of {savings_rate:.1f}% is healthy. Consider investing surplus.',
            'priority': 'low',
            'action': 'Explore investment opportunities',
            'potential_savings': 0
        })
    
    # Category-specific recommendations
    category_dict = dict(category_breakdown)
    
    if category_dict.get('Food', 0) > total_income * 0.25:
        recommendations.append({
            'title': 'Food Budget Optimization',
            'message': 'Food expenses are high. Try meal prep, local markets, and home cooking.',
            'priority': 'medium',
            'action': 'Reduce food spending by 20%',
            'potential_savings': category_dict.get('Food', 0) * 0.2
        })
    
    if category_dict.get('Entertainment', 0) > total_income * 0.15:
        recommendations.append({
            'title': 'Entertainment Budget Control',
            'message': 'Consider free activities and set entertainment budget limits.',
            'priority': 'medium',
            'action': 'Set monthly entertainment budget',
            'potential_savings': category_dict.get('Entertainment', 0) * 0.3
        })
    
    # Behavioral insights using AI-like analysis
    behavioral_insights = []
    
    if len(expenses) > 5:
        expense_amounts = [exp.amount for exp in expenses]
        avg_expense = statistics.mean(expense_amounts)
        std_expense = statistics.stdev(expense_amounts) if len(expense_amounts) > 1 else 0
        
        high_variance_expenses = [exp for exp in expenses if exp.amount > avg_expense + std_expense]
        
        if len(high_variance_expenses) > len(expenses) * 0.3:
            behavioral_insights.append({
                'pattern': 'Impulse Spending Detected',
                'description': 'You have irregular high-value expenses, suggesting impulse purchases.',
                'recommendation': 'Implement a 24-hour waiting period for purchases over ₹' + str(int(avg_expense)),
                'confidence': 85
            })
    
    # Check for recurring patterns
    if len(set(exp.category for exp in expenses)) < 4 and len(expenses) > 10:
        behavioral_insights.append({
            'pattern': 'Limited Spending Categories',
            'description': 'Your spending is concentrated in few categories, showing good discipline.',
            'recommendation': 'Maintain this focused approach but ensure you\'re not missing important categories like healthcare.',
            'confidence': 78
        })
    
    insights['ai_recommendations'] = recommendations
    insights['behavioral_insights'] = behavioral_insights
    
    # Future predictions (simple trend analysis)
    if len(monthly_trends) >= 2:
        trend_values = list(monthly_trends.values())
        if len(trend_values) >= 2:
            recent_trend = trend_values[-1] - trend_values[-2]
            insights['future_predictions'] = {
                'monthly_trend': recent_trend,
                'predicted_next_month': trend_values[-1] + recent_trend,
                'trend_direction': 'increasing' if recent_trend > 0 else 'decreasing'
            }
    
    return insights

@expense_bp.route('/insights', methods=['GET'])
def get_insights():
    try:
        expenses = Expense.query.all()
        incomes = Income.query.all()
        
        # Generate AI insights
        ai_insights = generate_ai_insights(expenses, incomes)
        
        # Legacy insights for compatibility
        total_expenses = sum(exp.amount for exp in expenses)
        total_income = sum(inc.amount for inc in incomes)  # Fixed: calculate total income
        net_balance = total_income - total_expenses  # Fixed: calculate net balance
        
        category_breakdown = defaultdict(float)
        for expense in expenses:
            category_breakdown[expense.category] += expense.amount
        
        # Income breakdown for frontend
        income_breakdown = defaultdict(float)
        for income in incomes:
            income_breakdown[income.source] += income.amount
        
        # Detect anomalies
        anomalies = []
        for category, total in category_breakdown.items():
            category_expenses = [exp for exp in expenses if exp.category == category]
            if len(category_expenses) > 1:
                amounts = [exp.amount for exp in category_expenses]
                avg_amount = sum(amounts) / len(amounts)
                for expense in category_expenses:
                    if expense.amount > avg_amount * 2:
                        anomalies.append({
                            'amount': expense.amount,
                            'category': expense.category,
                            'reason': f'This expense is {expense.amount/avg_amount:.1f}x higher than your average {category.lower()} expense of ₹{avg_amount:.2f}'
                        })

        return jsonify({
            'total_expenses': total_expenses,
            'total_income': total_income,  # Added missing field
            'net_balance': net_balance,  # Added missing field
            'savings_rate': (net_balance / total_income * 100) if total_income > 0 else 0,  # Added missing field
            'category_breakdown': dict(category_breakdown),
            'income_breakdown': dict(income_breakdown),  # Added income breakdown
            'anomalies': anomalies,
            'ai_insights': ai_insights,  # New AI-powered insights
            # Legacy recommendations for compatibility
            'recommendations': ai_insights.get('ai_recommendations', [])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== FINANCIAL DASHBOARD =====
@expense_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    try:
        expenses = Expense.query.all()
        incomes = Income.query.all()
        
        total_income = sum(inc.amount for inc in incomes)
        total_expenses = sum(exp.amount for exp in expenses)
        net_balance = total_income - total_expenses
        
        # Monthly breakdown
        monthly_data = defaultdict(lambda: {'income': 0, 'expenses': 0})
        
        for income in incomes:
            month_key = f"{income.date.year}-{income.date.month:02d}"
            monthly_data[month_key]['income'] += income.amount
            
        for expense in expenses:
            month_key = f"{expense.date.year}-{expense.date.month:02d}"
            monthly_data[month_key]['expenses'] += expense.amount
        
        # Convert to list for frontend
        monthly_chart_data = []
        for month, data in sorted(monthly_data.items()):
            monthly_chart_data.append({
                'month': month,
                'income': data['income'],
                'expenses': data['expenses'],
                'net': data['income'] - data['expenses']
            })
        
        return jsonify({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': net_balance,
            'monthly_data': monthly_chart_data,
            'savings_rate': (net_balance / total_income * 100) if total_income > 0 else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500