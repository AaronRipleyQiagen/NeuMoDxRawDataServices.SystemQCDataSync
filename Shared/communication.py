from flask_mail import Mail, Message
import requests
import os

system_qc_tech_IIs = {
    "Brian": "brian.colson1@contractor.qiagen.com",
    "Hunter": "hunter.rose1@contractor.qiagen.com",
    "Isaiah": "isaiah.thompson1@contractor.qiagen.com",
    "Keller": "keller.masing@contractor.qiagen.com",
    "Kyla": "kyla.tackett1@contractor.qiagen.com",
    "Nathan": "nathan.king1@contractor.qiagen.com",
    "Richie": "richard.wynn1@contractor.qiagen.com",
}
system_qc_reviewers = {
    "Leanna": "leanna.hoyer@qiagen.com",
    "Jeremias": "jeremias.lioi@qiagen.com",
}
system_integration_reviewers = {
    # "Catherine": "catherine.couture@qiagen.com",
    "Aaron": "aaron.ripley@qiagen.com",
}
engineering_reviewers = {"Vik": "viktoriah.slusher@qiagen.com"}
admin_reviewers = {"David": "david.edwin@qiagen.com"}


def send_review_ready_messages(app, runset_id, url, review_group_subscribers):
    server = app.server
    server.config["MAIL_SERVER"] = "smtp.gmail.com"
    server.config["MAIL_PORT"] = 465
    server.config["MAIL_USERNAME"] = "neumodxsystemqcdatasync@gmail.com"
    server.config["MAIL_PASSWORD"] = os.environ["EMAIL_PASSWORD"]
    server.config["MAIL_USE_TLS"] = False
    server.config["MAIL_USE_SSL"] = True
    mail = Mail(app.server)

    """
    Get reviewers to send email too
    """
    runset_url = os.environ["RUN_REVIEW_API_BASE"] + "RunSets/{}".format(runset_id)
    runset = requests.get(url=runset_url, verify=False).json()
    # if 'XPCR Module Qualification' in runset_type_selection_options[runset_type_selection_id]:
    msg = Message(
        runset["name"] + " Ready for review",
        sender="neumodxsystemqcdatasync@gmail.com",
        recipients=["aripley2008@gmail.com"],
    )
    url_substrings = url.split("/")
    runset_review_link_base = url_substrings[0] + "//" + url_substrings[2]
    runset_review_path = "/run-review/{}".format(runset_id)
    runset_review_link = runset_review_link_base + runset_review_path

    with mail.connect() as conn:
        for user in review_group_subscribers:
            message = (
                "Hello "
                + user
                + ", this message is sent to inform you that "
                + runset["name"]
                + " is now ready for your review. \n"
                + runset_review_link
            )
            subject = runset["name"] + " Ready for review"
            msg = Message(
                recipients=[review_group_subscribers[user]],
                body=message,
                subject=subject,
                sender="neumodxsystemqcdatasync@gmail.com",
            )

            conn.send(msg)
