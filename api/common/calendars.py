import requests

from rest_framework.exceptions import APIException


def create_calendar_event(user, summary, start_datetime, end_datetime, location):
    '''
    summary(string): 이벤트의 제목
    start_datetime(datetime): 이벤트 시작 시간 ex)2023-05-25T20:00:00+09:00
    end_datetime(datetime): 이벤트 종료 시간 ex)2023-05-25T22:00:00+09:00
    location(string): 이벤트의 지리적 위치
    '''
    if not hasattr(user, 'google_account'):
        raise APIException('this user did not sign in with google account.')

    request_uri = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
    body_data = {
        'summary': summary,
        'start': {
            'dateTime': start_datetime,
        },
        'end': {
            'dateTime': end_datetime,
        },
        'location': location,
    }

    access_token = user.google_account.access_token
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.post(request_uri, headers=headers, json=body_data)
    
    return response


def delete_calendar_event(user, event_id):
    if not hasattr(user, 'google_account'):
        raise APIException('this user did not sign in with google account.')

    request_uri = f'https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}'
    access_token = user.google_account.access_token
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.delete(request_uri, headers=headers)

    if response.status_code == 204:
        print('success')
    else:
        print('fail')
        print(response.json())

    return response

def update_calendar_event(user, event_id, summary, start_datetime, end_datetime, location):
    if not hasattr(user, 'google_account'):
        raise APIException('this user did not sign in with google account.')

    request_uri = f'https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}'
    body_data = {
        'summary': summary,
        'start': {
            'dateTime': start_datetime,
        },
        'end': {
            'dateTime': end_datetime,
        },
        'location': location,
    }

    access_token = user.google_account.access_token
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.put(request_uri, headers=headers, json=body_data)

    if response.status_code == 200:
        print('success')
    else:
        print('fail')
        print(response.json())

    return response
