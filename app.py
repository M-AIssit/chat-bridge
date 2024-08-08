from flask import Flask
from modules.api.users import create_user

app = Flask(__name__)

@app.route('/users', methods=['POST'])
def users():
    # Handle the logic for creating a user
    return create_user()

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run()
    