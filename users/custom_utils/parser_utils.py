import xml.etree.ElementTree as ET
from users import validator
from django.db import transaction


def xml_parser(file):
        try:
            tree = ET.parse(file)
            root = tree.getroot()

            users = []
            dublicate_data = set()

            with transaction.atomic():
                for user_item in root.findall('user'):
                    try:
                        first_name = user_item.find('first_name')
                        last_name = user_item.find('last_name')
                        email = user_item.find('email')
                        username = user_item.find("username")
                        password = user_item.find('password')


                        user_dict = {
                            "first_name": first_name.text if first_name is not None else None,
                            "last_name": last_name.text if last_name is not None else None,
                            "email": email.text if email is not None else None,
                            "username": username.text if username is not None else None,
                            "password": password.text if password is not None else None,
                        }

                        status , res_dict, dublicate = validator.validate_user(user_dict, dublicate_data)
                        dublicate_data = dublicate
                        users.append(res_dict)

                        
                        # last_name = user_item.find('last_name').text
                        # email = user_item.find('email').text
                        # username = user_item.find('username').text
                        # password = user_item.find('password').text

                        # print(first_name)
                        # print(last_name)
                        # print(email)
                        # print(username)
                        # print(password)
                    except Exception as e:
                        print("ERROR", e)
                        continue
                    

            return 'success', users


        except ET.ParseError as e:
            return 'error', e

        