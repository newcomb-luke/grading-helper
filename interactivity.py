def get_answer_yes_no():
    answer = None

    while answer is None:
        response = input('> ')

        if response == 'y':
            answer = True
        elif response == 'n':
            answer = False
        else:
            print('[INVALID RESPONSE]')

    return answer


def get_float():
    answer = None

    while answer is None:
        response = input('> ')

        try:
            answer = float(response)
        except:
            print('[INVALID FLOAT]')

    return answer
