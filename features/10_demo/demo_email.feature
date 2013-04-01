# language: en

@demo
Feature: Demonstrate the e-mail feature

  In order to demonstrate some features
  As an administrator
  I prepare and run some scenarii

  Background: the client is connected
    Given the user "admin" is connected
    And I execute the Python commands
    """
    ctx.data['values'] = {
        'email_from': 'admin@is.invalid',
        'email_to': 'sav@oerp.invalid',
        'subject': 'Subject',
        'body_text': 'Body'
    }
    """

  Scenario: Send an e-mail
    When I execute the Python commands
    """
    values = ctx.data['values']
    vals = (values['email_from'], [values['email_to']],
            values['subject'], values['body_text'])
    m1_id = model('mail.message').schedule_with_attach(*vals)
    m1 = model('mail.message').get(m1_id)
    ctx.data['message1'] = m1
    """
    Then no e-mail is sent
    When I execute the Python commands
    """
    m1 = ctx.data['message1']
    assert_equal(m1.state, 'outgoing')
    m1.send()
    m1.refresh()
    assert_equal(m1.state, 'sent')
    """
    Then an e-mail is sent from "admin@is.invalid" to "sav@oerp.invalid"
    When I execute the Python commands
    """
    m2 = ctx.data['message1'].copy()
    m2.mark_outgoing()
    assert_equal(m2.state, 'outgoing')
    m2.send()
    m2.send()
    m2.cancel()
    m2.send()
    m2.refresh()
    assert_equal(m2.state, 'sent')
    """
    Then 3 e-mails are sent
    When I execute the Python commands
    """
    m3 = ctx.data['message1'].copy()
    m3.cancel()
    assert_equal(m3.state, 'cancel')
    """
    Then no e-mail is sent

  Scenario: Compose and send an e-mail
    When I execute the Python commands
    """
    values = ctx.data['values']
    m1 = model('mail.compose.message').create(values)
    m1.send_mail()
    ctx.data['message1'] = m1
    """
    Then an e-mail is sent from "admin@is.invalid" to "sav@oerp.invalid"
    When I execute the Python commands
    """
    m1 = ctx.data['message1']
    m1.send_mail()
    m1.send_mail()
    m1.send_mail()
    """
    Then 3 e-mails are sent
    When I execute the Python commands
    """
    m1 = ctx.data['message1']
    m1.unlink()
    """
    Then no e-mail is sent

  Scenario: Low-level e-mail feature
    When I execute the Python commands
    """
    from email.MIMEText import MIMEText
    from email.MIMEMultipart import MIMEMultipart
    from email.Utils import make_msgid

    values = ctx.data['values']
    msg = MIMEMultipart()
    msg['Message-Id'] = make_msgid()
    msg['Subject'] = values['subject']
    msg['From'] = values['email_from']
    msg['To'] = values['email_to']
    body = MIMEText(values['body_text'], _subtype='plain', _charset='utf-8')
    msg.attach(body)
    assert_true(msg)

    message_id = model('ir.mail_server').send_email(msg)
    assert_equal(type(message_id), str)
    """
    Then an e-mail is sent from "admin@is.invalid" to "sav@oerp.invalid"
