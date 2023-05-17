from factory.django import DjangoModelFactory
from factory import sequence, Faker, SubFactory


TEST_PASSWORD = 'password'


class UserTypeFactory(DjangoModelFactory):
    class Meta:
        model = 'users.UserType'

    name = '학부생'
    possible_duration = 1

    @classmethod
    def create_admin_user_type(cls):
        return cls.create(id=1, name='조교', possible_duration=0)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = 'users.User'

    user_no = sequence(lambda n: f'1701111{n}')
    password = TEST_PASSWORD
    name = Faker('name', locale='ko_KR')
    email = Faker('email')
    user_type = SubFactory(UserTypeFactory)
