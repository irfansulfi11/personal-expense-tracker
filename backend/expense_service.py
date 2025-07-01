import os
import openai
from datetime import datetime, timedelta
from sqlalchemy import func
from ..models import db, Expense, Income

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

class ExpenseService:
    @staticmethod
    def get_monthly_summary():
        """Get monthly expense and income summary"""
        current_month = datetime.now().replace(day=1)
        
        # Get current month expenses
        monthly_expenses = db.session.query(
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.date >= current_month
        ).first()
        
        # Get current month income
        monthly_income = db.session.query(
            func.sum(Income.amount).label('total')
        ).filter(
            Income.date >= current_month
        ).first()
        
        return {
            'expenses': monthly_expenses.total or 0,
            'income': monthly_income.total or 0,
            'balance': (monthly_income.total or 0) - (monthly_expenses.total or 0)
        }
    
    @staticmethod
    def get_category_breakdown():
        """Get expense breakdown by category"""
        current_month = datetime.now().replace(day=1)
        
        category_data = db.session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.date >= current_month
        ).group_by(Expense.category).all()
        
        return [{'category': cat, 'amount': float(total)} for cat, total in category_data]
    
    @staticmethod
    def get_spending_trends():
        """Get last 6 months spending trends"""
        six_months_ago = datetime.now() - timedelta(days=180)
        
        trends = db.session.query(
            func.strftime('%Y-%m', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.date >= six_months_ago
        ).group_by(func.strftime('%Y-%m', Expense.date)).all()
        
        return [{'month': month, 'amount': float(total)} for month, total in trends]
    
    @staticmethod
    def generate_ai_insights():
        """Generate AI-powered financial insights"""
        try:
            # Get data for analysis
            summary = ExpenseService.get_monthly_summary()
            categories = ExpenseService.get_category_breakdown()
            trends = ExpenseService.get_spending_trends()
            
            # Prepare data for AI
            prompt = f"""
            Analyze this financial data and provide actionable insights:
            
            Monthly Summary:
            - Income: ${summary['income']}
            - Expenses: ${summary['expenses']}
            - Balance: ${summary['balance']}
            
            Category Breakdown: {categories}
            
            6-Month Trends: {trends}
            
            Please provide:
            1. 3 key insights about spending patterns
            2. 3 specific actionable recommendations
            3. 1 financial goal suggestion
            
            Keep response concise and practical.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a personal finance advisor. Provide clear, actionable advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return {
                'insights': response.choices[0].message.content,
                'summary': summary,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'insights': 'AI insights temporarily unavailable. Here are your key numbers: ' + 
                           f"Monthly balance: ${summary['balance']}, " +
                           f"Total expenses: ${summary['expenses']}",
                'summary': summary,
                'last_updated': datetime.now().isoformat(),
                'error': str(e)
            }
    
    @staticmethod
    def get_budget_alerts():
        """Check for budget alerts and recommendations"""
        summary = ExpenseService.get_monthly_summary()
        categories = ExpenseService.get_category_breakdown()
        
        alerts = []
        
        # Check if spending exceeds income
        if summary['balance'] < 0:
            alerts.append({
                'type': 'warning',
                'message': f"You're overspending by ${abs(summary['balance']):.2f} this month"
            })
        
        # Check for high category spending
        total_expenses = summary['expenses']
        if total_expenses > 0:
            for cat in categories:
                percentage = (cat['amount'] / total_expenses) * 100
                if percentage > 40:
                    alerts.append({
                        'type': 'info',
                        'message': f"{cat['category']} represents {percentage:.1f}% of your spending"
                    })
        
        return alerts