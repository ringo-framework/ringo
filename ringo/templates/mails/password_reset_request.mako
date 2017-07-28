${_('Dear user')},

${_('You have received this email because you requested the reset of your password for ${app_name}: ${username}.', mapping={'app_name': app_name, 'username':username})|n}


${_('To complete the reset of your password you need to confirm reset by clicking the following link:')}
${url}

${_('After you clicked on the link the password will be reseted and an email with the new password will be send to you.')}

${_('kind regards')}
${_('your ${app_name} team', mapping={'app_name': app_name})}

${_('This email was sent automatically. Please do not reply on this email. In case of questions please send an email to ${email}.', mapping={'email': email})}
