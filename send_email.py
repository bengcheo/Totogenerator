import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def load_toto_numbers():
    """Load generated TOTO numbers from file"""
    try:
        with open('toto_numbers.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def create_email_html(toto_data):
    """Create HTML email content"""
    if not toto_data:
        return "<p>No TOTO numbers were generated.</p>"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ color: #2c5aa0; text-align: center; }}
            .numbers {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            .set {{ margin: 10px 0; padding: 10px; border-left: 4px solid #28a745; }}
            .footer {{ color: #666; font-size: 12px; text-align: center; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎲 Your TOTO Numbers</h1>
            <p>Generated on {toto_data['date']} at {datetime.now().strftime('%H:%M:%S')} UTC</p>
        </div>
        
        <div class="numbers">
            <h2>Lucky Numbers for Next Draw:</h2>
    """
    
    for set_data in toto_data['sets']:
        html += f"""
            <div class="set">
                <strong>Set {set_data['set']}:</strong> 
                <span style="font-size: 18px; color: #dc3545; letter-spacing: 2px;">
                    {set_data['formatted']}
                </span>
            </div>
        """
    
    html += f"""
        </div>
        
        <div class="footer">
            <p>🍀 Good luck with your TOTO play!</p>
            <p><em>Generated {toto_data['total_sets']} sets • Remember to play responsibly</em></p>
        </div>
    </body>
    </html>
    """
    
    return html

def send_email():
    """Send email with TOTO numbers"""
    
    # Get email credentials from environment variables (GitHub secrets)
    sender_email = os.getenv('EMAIL_USER')
    sender_password = os.getenv('EMAIL_PASSWORD')
    
    # Set your recipient email here
    recipient_email = "sebastian_bc_cheong@outlook.com"
    
    if not sender_email or not sender_password:
        print("⚠️  Email credentials not found in environment variables")
        print("Make sure to set EMAIL_USER and EMAIL_PASSWORD in GitHub secrets")
        return False
    
    # Load TOTO numbers
    toto_data = load_toto_numbers()
    
    try:
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎲 Your TOTO Numbers - {datetime.now().strftime('%Y-%m-%d')}"
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # Create HTML content
        html_content = create_email_html(toto_data)
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email via Gmail
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print("✅ Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    success = send_email()
    if not success:
        exit(1)
