from app import create_app
import os

# Explicitly set static_folder and static_url_path
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = create_app()
app.static_folder = static_folder
app.static_url_path = '/static'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5010) 