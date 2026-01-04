from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>CPF Crime Reporting System - Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 40px;
                text-align: center;
                background-color: #f5f5f5;
            }
            h1 {
                color: #003366;
                margin-bottom: 30px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .status {
                background-color: #e6f7ff;
                border-left: 5px solid #1890ff;
                padding: 15px;
                margin-bottom: 20px;
                text-align: left;
            }
            ul {
                list-style-type: none;
                padding: 0;
                text-align: left;
            }
            li {
                margin-bottom: 10px;
            }
            .feature {
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CPF Crime Reporting System</h1>
            
            <div class="status">
                <h3>Docker Test App Working!</h3>
                <p>This is a simple Flask test application to verify that Docker is working properly.</p>
            </div>
            
            <h2>System Features</h2>
            <ul>
                <li><span class="feature">Crime Reporting:</span> Citizens can report incidents online</li>
                <li><span class="feature">Dashboard:</span> Interactive statistics and analytics</li>
                <li><span class="feature">Community Alerts:</span> Real-time emergency notifications</li>
                <li><span class="feature">Event Calendar:</span> Community policing events</li>
                <li><span class="feature">User Profiles:</span> Manage notification preferences</li>
            </ul>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
