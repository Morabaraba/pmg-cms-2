from itertools import groupby

from flask import url_for

MIN_YEAR = 2006


ICONS = {
    "member": "bill-introduced.png",
    "committee": "committee-discussion.png",
    "house": "house.png",
    "president": "signed-by-president.png",
    "unknown": "bill-introduced.png",
    }

def get_location(event):
    if event['type'] in ['bill-signed', 'bill-act-commenced', 'bill-enacted']:
        return {
            'name': 'Office of the President',
            'class': 'president',
            }

    if 'house' in event:
        return {
            'name': event['house']['name'],
            'class': event['house']['name_short'],
            }

    if 'committee' in event:
        if 'house' in event['committee']:
            return {
                'name': event['committee']['house']['name'],
                'class': event['committee']['house']['name_short'],
                }

        return {
            'name': event['committee']['name'],
            'url': url_for('committee_detail', committee_id=event['committee']['id']),
            'class': '',
        }

    return {'name': 'Unknown', 'class': ''}

def get_agent(event, bill):
    info = None

    if event['type'] in ['bill-signed', 'bill-act-commenced', 'bill-enacted']:
        info = {
            'name': 'The President',
            'type': 'president',
        }

    elif event['type'] == 'bill-introduced':
        info = {
            'name': bill['introduced_by'] or bill.get('place_of_introduction', {}).get('name'),
            'type': 'member',
        }

    elif 'member' in event:
        info = {
            'name': event['member']['name'],
            'type': 'member',
            'url': url_for('member', member_id=event['member']['id'])
        }

    elif 'committee' in event:
        info = {
            'name': event['committee']['name'],
            'type': 'committee',
            'url': url_for('committee_detail', committee_id=event['committee']['id'])
        }

    elif 'house' in event:
        info = {
            'name': event['house']['name'],
            'type': 'house',
            }
    else:
        info = {'name': 'Unknown', 'type': 'unknown'}


    info['icon'] = ICONS[info['type']]

    return info


def bill_history(bill):
    """ Work out the history of a bill and return a description of it. """
    history = []

    events = bill.get('events', [])
    events.sort(key=lambda e: [e['date'], get_location(e), get_agent(e, bill)])

    for location, location_events in groupby(events, get_location):
        location_history = []

        for agent, agent_events in groupby(location_events, lambda e: get_agent(e, bill)):
            info = {'events': list(agent_events)}
            info.update(agent)
            location_history.append(info)

        info = {'events': location_history}
        info.update(location)
        history.append(info)

    return history
