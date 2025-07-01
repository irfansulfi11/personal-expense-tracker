from api import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Ensure database tables are created
    with app.app_context():
        from api.models.expense import db
        db.create_all()
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)