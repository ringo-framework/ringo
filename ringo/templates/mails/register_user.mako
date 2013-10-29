${_('Dear user')},

${_('You have received this email because you registered for "${app_name}".', mapping={'app_name': app_name})}

${_('To complete the registration you need to confirm the registration by clicking the following link:')}
${url}

${_('kind regards')}
${_('your ${app_name} team', mapping={'app_name': app_name})}

${_('This email was sent automatically. Please do not reply on this email. In case of questions please send an email to ${email}.', mapping={'email': email})}
