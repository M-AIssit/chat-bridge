from flask import Flask
from modules.api.users import create_user
from modules.api.users3 import handle_incoming_message


app = Flask(__name__)

@app.route('/users', methods=['POST'])
def users():
    # Handle the logic for creating a user
    return handle_incoming_message()
    #return create_user()

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run()
    