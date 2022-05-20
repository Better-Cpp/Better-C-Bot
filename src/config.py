# Elevated permissions
permitted = [976621757798694932]
staff_role = 976621757798694932

# General
max_msg_size = 2000
no_react = "❎"
yes_react = "✅"

# Bot detection
massjoin_window = 30
massjoin_amount = 5
massjoin_notif_timeout = 900
massjoin_wizard_timeout = 300
massjoin_default_pfp = True
massjoin_min_acc_age = True
massjoin_min_acc_age_val = 604800

# Bump notifier
bump_bot_id = 302050872383242240
bump_bot_content = "Bump done"
bumper_role_id = 873897990958481448

# Duplicate message detection
dupe_thresh = 0.8

# Rule scanner
rules_channel = 583301260006916099

# Delted message sniping
max_del_msgs = 10
max_edit_msg_age = 86400

help_categories = {
  'available': 976922937791741982,
  'occupied': 976923113554067496,
  'dormant': 976923166930788382
}

from datetime import timedelta

# how often to recheck whether a help channel has become dormant
# in seconds
recheck_time = 5

# after how much time an occupied channel will become dormant
dormant_time = timedelta(seconds=20)

# after how much time a dormant channel will be available again
reset_time = timedelta(seconds=60)