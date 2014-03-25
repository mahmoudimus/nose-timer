import termcolor


def colored_time(time_taken, options):
    """Get colored string for a given time taken."""
    time_taken_ms = time_taken * 1000
    if time_taken_ms <= options.timer_ok:
        color = 'green'
    elif time_taken_ms <= options.timer_warning:
        color = 'yellow'
    else:
        color = 'red'
    return termcolor.colored("{0:0.4f}s".format(time_taken), color)
