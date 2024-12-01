def coop_policy_middleware(get_response):
    def middleware(request):
        # Получаем ответ от следующего промежуточного ПО
        response = get_response(request)
        
        # Устанавливаем заголовок Cross-Origin-Opener-Policy
        response['Cross-Origin-Opener-Policy'] = 'same-origin'  # Только для того же источника
        
        return response

    return middleware