from datetime import timedelta

# Elevated permissions
# John, Che, Andy, Gemu
permitted = [553478921870508061, 176681843356073985, 806272111076835381, 135215807532630016]
staff_role = 583646707938623489

# General
max_msg_size = 2000
max_msg_embeds_size = 6000
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

# Deleted message sniping
max_del_msgs = 10
max_edit_msg_age = timedelta(days=1)

ping_role = 873897990958481448

# Role that can reactivate and close help channels without having to own the channel
helpful_role = 983185446047719504

help_channel = 1045182836107395124

closeable = {
  help_channel : 'Done', # help
  1055500115432972318 : 'Done'  # code-review
}
