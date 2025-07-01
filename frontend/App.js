import React, { useState, useEffect } from 'react';
import { expenseAPI } from './services/api';
import './App.css';

function App() {
  const [expenses, setExpenses] = useState([]);
  const [incomes, setIncomes] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('expenses');
  
  const [newExpense, setNewExpense] = useState({
    category: '',
    amount: '',
    description: '',
    date: new Date().toISOString().split('T')[0]
  });

  const [newIncome, setNewIncome] = useState({
    source: '',
    amount: '',
    description: '',
    date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [expensesResponse, incomesResponse, insightsResponse] = await Promise.all([
        expenseAPI.getExpenses(),
        expenseAPI.getIncomes(),
        expenseAPI.getInsights()
      ]);

      setExpenses(expensesResponse.data);
      setIncomes(incomesResponse.data);
      setInsights(insightsResponse.data);
    } catch (err) {
      console.error('Failed to load data:', err);
      setError('Failed to load data. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleExpenseSubmit = async (e) => {
    e.preventDefault();

    if (!newExpense.category || !newExpense.amount) {
      alert('Please fill in category and amount');
      return;
    }

    try {
      await expenseAPI.createExpense({
        ...newExpense,
        amount: parseFloat(newExpense.amount)
      });

      setNewExpense({
        category: '',
        amount: '',
        description: '',
        date: new Date().toISOString().split('T')[0]
      });

      loadData();
    } catch (err) {
      console.error('Failed to create expense:', err);
      alert('Failed to create expense');
    }
  };

  const handleIncomeSubmit = async (e) => {
    e.preventDefault();

    if (!newIncome.source || !newIncome.amount) {
      alert('Please fill in source and amount');
      return;
    }

    try {
      await expenseAPI.createIncome({
        ...newIncome,
        amount: parseFloat(newIncome.amount)
      });

      setNewIncome({
        source: '',
        amount: '',
        description: '',
        date: new Date().toISOString().split('T')[0]
      });

      loadData();
    } catch (err) {
      console.error('Failed to create income:', err);
      alert('Failed to create income');
    }
  };

  const handleExpenseDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this expense?')) {
      try {
        await expenseAPI.deleteExpense(id);
        loadData();
      } catch (err) {
        console.error('Failed to delete expense:', err);
        alert('Failed to delete expense');
      }
    }
  };

  const handleIncomeDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this income?')) {
      try {
        await expenseAPI.deleteIncome(id);
        loadData();
      } catch (err) {
        console.error('Failed to delete income:', err);
        alert('Failed to delete income');
      }
    }
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <div className="error">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={loadData}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Personal Finance Tracker</h1>
        <div className="header-stats">
          {insights && (
            <>
              <div className="stat">
                <span className="stat-label">Total Income:</span>
                <span className="stat-value income">₹{insights.total_income?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Total Expenses:</span>
                <span className="stat-value expense">₹{insights.total_expenses?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Net Balance:</span>
                <span className={`stat-value ${insights.net_balance >= 0 ? 'positive' : 'negative'}`}>
                  ₹{insights.net_balance?.toFixed(2) || '0.00'}
                </span>
              </div>
            </>
          )}
        </div>
      </header>

      <main className="app-main">
        {/* Enhanced AI Insights Section */}
        {insights && (
          <section className="insights">
            <h2>AI Financial Insights</h2>
            <div className="insights-grid">
              <div className="insight-card overview">
                <h3>Financial Overview</h3>
                <div className="overview-stats">
                  <div className="overview-item">
                    <span>Savings Rate:</span>
                    <span className={insights.savings_rate >= 20 ? 'good' : 'warning'}>
                      {insights.savings_rate?.toFixed(1) || '0.0'}%
                    </span>
                  </div>
                  <div className="overview-item">
                    <span>Top Expense Category:</span>
                    <span>{insights.top_expense_category || 'N/A'}</span>
                  </div>
                  <div className="overview-item">
                    <span>Top Income Source:</span>
                    <span>{insights.top_income_source || 'N/A'}</span>
                  </div>
                </div>
              </div>

              {insights.financial_health && (
                <div className="insight-card health">
                  <h3>Financial Health</h3>
                  <div className={`health-score ${insights.financial_health.status}`}>
                    <div className="score">{insights.financial_health.score}/100</div>
                    <div className="status">{insights.financial_health.status.toUpperCase()}</div>
                  </div>
                  <p>{insights.financial_health.message}</p>
                </div>
              )}

              {insights.ai_recommendations?.length > 0 && (
                <div className="insight-card recommendations">
                  <h3>AI Recommendations</h3>
                  <div className="recommendations-list">
                    {insights.ai_recommendations.map((rec, index) => (
                      <div key={index} className={`recommendation ${rec.priority}`}>
                        <div className="rec-header">
                          <span className="rec-icon">{rec.priority === 'high' ? '🚨' : rec.priority === 'medium' ? '⚠️' : 'ℹ️'}</span>
                          <h4>{rec.title}</h4>
                        </div>
                        <p>{rec.message}</p>
                        {rec.action && <div className="rec-action">💡 {rec.action}</div>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="insight-card breakdown">
                <h3>Category Breakdown</h3>
                <div className="breakdown-container">
                  <div className="breakdown-section">
                    <h4>Expenses</h4>
                    <div className="category-breakdown">
                      {Object.entries(insights.category_breakdown || {}).map(([category, amount]) => (
                        <div key={category} className="category-item">
                          <span>{category}</span>
                          <span>₹{amount.toFixed(2)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="breakdown-section">
                    <h4>Income Sources</h4>
                    <div className="category-breakdown">
                      {Object.entries(insights.income_breakdown || {}).map(([source, amount]) => (
                        <div key={source} className="category-item">
                          <span>{source}</span>
                          <span>₹{amount.toFixed(2)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {insights.trends && (
                <div className="insight-card trends">
                  <h3>Spending Trends</h3>
                  <div className="trends-list">
                    {Object.entries(insights.trends).map(([period, trend]) => (
                      <div key={period} className="trend-item">
                        <span className="trend-period">{period}:</span>
                        <span className={`trend-value ${trend.direction}`}>
                          {trend.direction === 'up' ? '📈' : '📉'} {trend.change}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {insights.anomalies?.length > 0 && (
                <div className="insight-card anomalies">
                  <h3>Unusual Activity Detected</h3>
                  <div className="anomalies-list">
                    {insights.anomalies.map((anomaly, index) => (
                      <div key={index} className="anomaly">
                        <p><strong>₹{anomaly.amount}</strong> - {anomaly.category}</p>
                        <p className="reason">{anomaly.reason}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </section>
        )}

        {/* Navigation Tabs */}
        <section className="navigation-tabs">
          <div className="tabs">
            <button 
              className={`tab ${activeTab === 'expenses' ? 'active' : ''}`}
              onClick={() => setActiveTab('expenses')}
            >
              📤 Expenses ({expenses.length})
            </button>
            <button 
              className={`tab ${activeTab === 'income' ? 'active' : ''}`}
              onClick={() => setActiveTab('income')}
            >
              📥 Income ({incomes.length})
            </button>
          </div>
        </section>

        {/* Expense Management */}
        {activeTab === 'expenses' && (
          <>
            <section className="add-expense">
              <h2>Add New Expense</h2>
              <form onSubmit={handleExpenseSubmit} className="expense-form">
                <div className="form-group">
                  <label>Category:</label>
                  <select
                    value={newExpense.category}
                    onChange={(e) => setNewExpense({ ...newExpense, category: e.target.value })}
                    required
                  >
                    <option value="">Select Category</option>
                    <option value="Food">🍽️ Food</option>
                    <option value="Transport">🚗 Transport</option>
                    <option value="Entertainment">🎬 Entertainment</option>
                    <option value="Shopping">🛍️ Shopping</option>
                    <option value="Utilities">⚡ Utilities</option>
                    <option value="Healthcare">🏥 Healthcare</option>
                    <option value="Education">📚 Education</option>
                    <option value="Investment">📈 Investment</option>
                    <option value="Other">📦 Other</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Amount (₹):</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newExpense.amount}
                    onChange={(e) => setNewExpense({ ...newExpense, amount: e.target.value })}
                    placeholder="Enter amount in rupees"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Description:</label>
                  <input
                    type="text"
                    value={newExpense.description}
                    onChange={(e) => setNewExpense({ ...newExpense, description: e.target.value })}
                    placeholder="Optional description"
                  />
                </div>

                <div className="form-group">
                  <label>Date:</label>
                  <input
                    type="date"
                    value={newExpense.date}
                    onChange={(e) => setNewExpense({ ...newExpense, date: e.target.value })}
                    required
                  />
                </div>

                <button type="submit" className="btn-primary">Add Expense</button>
              </form>
            </section>

            <section className="expenses-list">
              <h2>Recent Expenses ({expenses.length})</h2>
              {expenses.length === 0 ? (
                <p className="no-data">No expenses recorded yet. Add your first expense above!</p>
              ) : (
                <div className="data-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Category</th>
                        <th>Description</th>
                        <th>Amount</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {expenses
                        .sort((a, b) => new Date(b.date) - new Date(a.date))
                        .map((expense) => (
                          <tr key={expense.id}>
                            <td>{expense.date}</td>
                            <td>{expense.category}</td>
                            <td>{expense.description || '-'}</td>
                            <td className="amount expense">₹{expense.amount.toFixed(2)}</td>
                            <td>
                              <button
                                onClick={() => handleExpenseDelete(expense.id)}
                                className="btn-danger"
                              >
                                Delete
                              </button>
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </>
        )}

        {/* Income Management */}
        {activeTab === 'income' && (
          <>
            <section className="add-income">
              <h2>Add New Income</h2>
              <form onSubmit={handleIncomeSubmit} className="income-form">
                <div className="form-group">
                  <label>Source:</label>
                  <select
                    value={newIncome.source}
                    onChange={(e) => setNewIncome({ ...newIncome, source: e.target.value })}
                    required
                  >
                    <option value="">Select Source</option>
                    <option value="Salary">💼 Salary</option>
                    <option value="Freelance">💻 Freelance</option>
                    <option value="Business">🏢 Business</option>
                    <option value="Investment">📈 Investment</option>
                    <option value="Rental">🏠 Rental</option>
                    <option value="Gift">🎁 Gift</option>
                    <option value="Bonus">💰 Bonus</option>
                    <option value="Other">📦 Other</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Amount (₹):</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newIncome.amount}
                    onChange={(e) => setNewIncome({ ...newIncome, amount: e.target.value })}
                    placeholder="Enter amount in rupees"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Description:</label>
                  <input
                    type="text"
                    value={newIncome.description}
                    onChange={(e) => setNewIncome({ ...newIncome, description: e.target.value })}
                    placeholder="Optional description"
                  />
                </div>

                <div className="form-group">
                  <label>Date:</label>
                  <input
                    type="date"
                    value={newIncome.date}
                    onChange={(e) => setNewIncome({ ...newIncome, date: e.target.value })}
                    required
                  />
                </div>

                <button type="submit" className="btn-primary income">Add Income</button>
              </form>
            </section>

            <section className="incomes-list">
              <h2>Recent Income ({incomes.length})</h2>
              {incomes.length === 0 ? (
                <p className="no-data">No income recorded yet. Add your first income above!</p>
              ) : (
                <div className="data-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Source</th>
                        <th>Description</th>
                        <th>Amount</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {incomes
                        .sort((a, b) => new Date(b.date) - new Date(a.date))
                        .map((income) => (
                          <tr key={income.id}>
                            <td>{income.date}</td>
                            <td>{income.source}</td>
                            <td>{income.description || '-'}</td>
                            <td className="amount income">₹{income.amount.toFixed(2)}</td>
                            <td>
                              <button
                                onClick={() => handleIncomeDelete(income.id)}
                                className="btn-danger"
                              >
                                Delete
                              </button>
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;