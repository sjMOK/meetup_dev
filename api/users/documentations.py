from rest_framework import serializers

from .serializers import UserTypeSerializer, UserDepartmentSerializer


not_found_response = '"detail": "Not found."'


logout_view_operation_description = '''
쿠키로 넘긴 sessionid의 유저 로그아웃
sessionid에 대응되는 세션 데이터 서버에서 삭제 후 쿠키 삭제, csrftoken은 쿠키에서 삭제하지 않음
성공시 200 응답, 쿠키에 sessionid가 존재하지 않아도 200 응답(이 경우 서버에서 아무 작업도 하지 않음)
'''


login_view_operation_description = '''
body data의 user_no와 password에 일치하는 유저 로그인
유저의 세션 데이터 생성 후 해당 세션의 id를 쿠키에 담아서 response 반환 - 헤더의 Set-Cookie sessionid 확인
user_no와 password에 일치하는 유저 없을 시 400 에러(No matching user.)
쿠키에 이미 발급 받은 세션 담아서 보낼 경우 해당 세션의 만료 기한 연장 후 반환
'''


change_password_operation_description = '''
user 비밀번호 변경 요청
body의 current_password와 user의 현재 비밀번호가 일치해야 하며 현재 비밀번호와 변경하고자 하는 비밀번호가 달라야함
'''


user_create_operation_description = '''
user 생성 요청
body의 필드가 잘못된 형식일 경우 해당 필드 이름이 key, 이유가 value인 메세지와 함께 400 반환
'''


user_partial_update_operation_description = '''
user 데이터 변경 요청
변경할 필드만 body에 담으면 됨
body의 필드가 잘못된 형식일 경우 해당 필드 이름이 key, 이유가 value인 메세지와 함께 400 반환
일반 유저의 경우 name(이름), email(이메일)만 변경 가능, admin 유저의 경우 user_no(학번/교번), user_type(타입)도 변경 가능
'''


user_bulk_create_operation_description = '''
user 다중 생성

지정된 양식의 csv파일을 http body에 form 형식으로 전달. 이 때 key는 user_input
key의 이름이 잘못되면 400 반환

csv 파일 전달에 성공하면 200과 함께 csv 형식의 데이터가 반환되는데, 
데이터의 형식이 정확하고 user_no의 중복 검사가 성공하면 'user_no_duplicated'와 'errors' 열이 비어있으며 유저가 생성됨
실패하면 'user_no_duplicated'와 'errors' 열에 값이 채워져 있으며 아무런 유저가 생성되지 않음

user_no_duplicated: 입력 데이터의 user_no에 중복된 값들이 존재
errors: data의 형식이 잘못됐으며(이메일 형식, 이미 존재하는 user_no, user_type 또는 department의 잘못된 id 등) 그 사유가 값으로 출력
'''


user_bulk_delete_operation_description = '''
user 다중 삭제
삭제하고자 하는 user_no를 개행으로 구분하여 http body에 text 전달, header에 Content-Type: text/plain로 전달
ex)
17011111
17011112
17011113
17011114
17011115
'''


class UserResponse(serializers.Serializer):
    id = serializers.IntegerField()
    user_no = serializers.CharField()
    name = serializers.CharField()
    email = serializers.CharField()
    user_type = UserTypeSerializer()
    deparment = UserDepartmentSerializer()


class UserListResponse(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = UserResponse(many=True)
