import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
from database import execute_query
from config import SMTP_CONFIG, ADMIN_EMAIL, REPORT_DIR
import logging

logger = logging.getLogger(__name__)


def get_visit_data(start_date, end_date):
    """Fetches customer visit data within a date range."""
    query = """
        SELECT unique_id, name, email, last_visited, visit_count
        FROM customers
        WHERE DATE(last_visited) BETWEEN %s AND %s
        ORDER BY last_visited DESC
    """
    return execute_query(query, (start_date, end_date), fetch_all=True)


def generate_csv_report(start_date, end_date):
    """Generates a CSV report and returns its path."""
    data = get_visit_data(start_date, end_date)
    if not data:
        logger.warning(f"No visit data found for range {start_date} to {end_date}.")
        return None

    try:
        df = pd.DataFrame(data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"visit_report_{timestamp}.csv"
        filepath = os.path.join(REPORT_DIR, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Report generated: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to generate CSV report: {e}")
        return None


def send_email_with_attachment(to_email, subject, body, attachment_path):
    """Sends an email with an attachment using SMTP."""
    cfg = SMTP_CONFIG
    if not all([cfg.get("server"), cfg.get("user"), cfg.get("password"), to_email]):
        logger.error("SMTP not configured or no admin email set. Cannot send email.")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = cfg["user"]
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        if attachment_path and os.path.exists(attachment_path):
            filename = os.path.basename(attachment_path)
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            msg.attach(part)
        else:
            logger.warning("Attachment path not provided or does not exist.")

        server = smtplib.SMTP(cfg["server"], cfg["port"])
        server.starttls()
        server.login(cfg["user"], cfg["password"])
        text = msg.as_string()
        server.sendmail(cfg["user"], to_email, text)
        server.quit()
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error(
            "SMTP Authentication Error. Check username/password (especially App Password for Gmail)."
        )
        return False
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def generate_and_email_report(start_date, end_date):
    """Generates and emails the report to the admin."""
    if not ADMIN_EMAIL:
        return {"status": "error", "message": "Admin email not configured."}

    filepath = generate_csv_report(start_date, end_date)
    if not filepath:
        return {"status": "error", "message": "No data found for the selected period."}

    subject = f"Customer Visit Report ({start_date} to {end_date})"
    body = f"Please find attached the customer visit report for the period {start_date} to {end_date}."

    if send_email_with_attachment(ADMIN_EMAIL, subject, body, filepath):
        return {"status": "success", "message": f"Report sent to {ADMIN_EMAIL}."}
    else:
        return {"status": "error", "message": "Failed to send the report email."}
