
# get activity info
def get_activity():
    pass



# accept activity
def accept_activity():
    pass



function_register = {
    ('/activity/activity_id', 'GET'): get_activity,
    ('/activity/status/activity_id', 'PUT'): accept_activity
}
