

# AUTH

# POST /auth/magic-link
# check it is an email
# check allowlist from env
# create hashed token, send email, log URL
# return 200 with the generic message

# POST /auth/verify
# hash incoming token and look up
# reject if not found, used, or expired
# set used_at
# create session
# set cookie, e.g session=raw_session_token

# POST /auth/logout 
# delete session
# delete cookie