import base
from web import models


def run():
    models.PricePolicy.objects.create(
        title='VIP',
        price=100,
        project_num=50,
        person_num=10,
        project_space=10,
        per_file_size=500,
        category=2
    )

    models.PricePolicy.objects.create(
        title='SVIP',
        price=200,
        project_num=150,
        person_num=110,
        project_space=110,
        per_file_size=1024,
        category=2
    )

    models.PricePolicy.objects.create(
        title='SSVIP',
        price=500,
        project_num=550,
        person_num=510,
        project_space=510,
        per_file_size=2048,
        category=2
    )


if __name__ == '__main__':
    run()