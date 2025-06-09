import re
from users.models import User


def create_field(value=None, valid=True, error=None):
    return {"value": value, "valid": valid, "error": error}


def validate_user(data: dict, dublicate=None):
    dublicate_set = dublicate if isinstance(dublicate, set) else set()

    try:
        first_name = data["first_name"] if data['first_name'] is not None else None
        last_name = data["last_name"] if data["last_name"] is not None else None
        email = data["email"] if data["email"] is not None else None
        username = data["username"] if data["username"] is not None else None
        password = data["password"] if data["password"] is not None else None
    except Exception as e:
        return "error", {}
    
    res = {
        "first_name": create_field(first_name),
        "last_name": create_field(last_name),
        "email": create_field(email),
        "username": create_field(username),
        "password": create_field(password),
        "overal_valid": True,
    }
    
    if first_name is None:
        res["first_name"]['value'] = 'None'
        res['first_name']['valid'] = False
        res['first_name']['error'] = "Відсутнє поле Ім`я"
        res['overal_valid'] = False

    if last_name is None:
        res["last_name"]['value'] = 'None'
        res['last_name']['valid'] = False
        res['last_name']['error'] = "Відсутнє поле Прізвище"
        res['overal_valid'] = False

    
    if username is None:
        if first_name:
            user_first_name = first_name
        else:
            user_first_name = 'n'

        if last_name:
            user_last_name = last_name
        else:
            user_last_name = 'student'

        test_username = f"{user_first_name[0]}{user_last_name}"
        res_username = test_username
        index = 0

        while User.objects.filter(username=res_username).exists():
            res_username = f"{index}-{test_username}"
            index += 1

        print('RES username', res_username)
        res['username']['value'] = res_username
    else:
        if dublicate:
            if str(username).lower().strip() in dublicate:
                res['username']['valid'] = False
                res['username']['error'] = 'Дублікат поля username'
                res['overal_valid'] = False
            else:
                if User.objects.filter(username=username).exists():
                    res['username']['valid'] = False
                    res['username']['error'] = 'Користувач з таким username вже існує'
                    res['overal_valid'] = False
                else:
                    dublicate_set.add(str(username).lower().strip())

        else:
            if User.objects.filter(username=username).exists():
                res['username']['valid'] = False
                res['username']['error'] = 'Користувач з таким username вже існує'
                res['overal_valid'] = False
            else:
                dublicate_set.add(str(username).lower().strip())
    

    if email:
        if dublicate:
            if str(email).lower().strip() in dublicate:
                res['email']['valid'] = False
                res['email']['error'] = 'Дублікат поля email'
                res['overal_valid'] = False
            else:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

                if not re.fullmatch(email_pattern, str(email)):
                    res["email"]['valid'] = False
                    res["email"]['error'] = "Невірний формат email"
                    res['overal_valid'] = False
                else:
                    if User.objects.filter(email=email).exists():
                        res["email"]['valid'] = False
                        res["email"]['error'] = "Такий email вже існує"
                        res['overal_valid'] = False
                    else:
                        dublicate_set.add(str(email).lower().strip())

        else:
            if User.objects.filter(email=email).exists():
                res["email"]['valid'] = False
                res["email"]['error'] = "Такий email вже існує"
                res['overal_valid'] = False
            else:
                dublicate_set.add(str(email).lower().strip())

    else:
        res["email"]['value'] = 'None'
        res["email"]['valid'] = False
        res["email"]['error'] = "Відсутнє поле email"
        res['overal_valid'] = False

    
    if password:
        
        if len(str(password).strip()) < 5:
            res["password"]['value'] = '-'
            res["password"]['valid'] = False
            res['password']['error'] = "Пароль повинен будти не менш ніж 5 символів"
            res['overal_valid'] = False

    else:
        res["password"]['value'] = 'None'
        res["password"]['valid'] = False
        res['password']['error'] = "Відсутнє поле password"
        res['overal_valid'] = False


    
    return "ok", res, dublicate_set
        
        
        