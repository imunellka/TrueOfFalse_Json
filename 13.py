from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

cities = [
    'да$Правда ли, что у осьминогов прямоугольные зрачки?$965417/f01f22030e1f3bf06038',
    'нет$Правда ли, что из-за особого рациона кровь у летучей мыши не красного, а голубого цвета?$1521359/76d182e30659f27364f7',
    'да$Правда ли, что дикобраз может пораниться собственными иглами?$1652229/f6908778c8c3f760c3cf',
    'нет$Правда ли, что изюм содержит в своём составе тетрагидроканнабинол и поэтому запрещён к ввозу в Судан и Филиппины?$997614/1dbf4ed97ab532944632',
    'нет$Правда ли, что на побережье Хабаровского края произрастает морозоустойчивый вид пальм?$997614/38ba2b77c584c289a970',
    'да$Правда ли, что бамбук цветёт примерно раз в 60 лет?$997614/b2c3debff76878abb0da',
    'да$Правда ли, что российская река Делькю несёт свои воды сразу в два океана?$1030494/b7c73a4aa3e68d54911e',
    'да$Эйфелева башня летом становится выше на 15 сантиметров$1540737/b27f647f00736240af9a',
    'да$Блоха может разгоняться быстрее, чем космический шаттл$1656841/5e917c8202eb52bb8611',
    'нет$ДНК человека и банана схожи на 90%$997614/082e8d09b1342dcaaf28',
    'да$Люди не могут дышать и глотать одновременно$1533899/73ec759e01edfed9e779',
    'нет$У осьминога два сердца$1540737/d62e342a66749ed73db0',
    'да$Если вы заплачете в космосе, то слёзы просто прилипнут к вашему лицу$1533899/2b249e2d47388f4fbd88',
    'да$Владелец компании, которая делает сегвеи, умер из-за того, что упал с обрыва на сегвее$937455/62539da43abaad112923',
    'нет$Молния никогда не ударяет в одно и то же место дважды$213044/7bb84b9b0726fdacec67',

    'нет$Евразия - самый влажный материк$1540737/10a1ccf66b747ef0e18d',
    'нет$Хартум - столица Египта$1652229/6417d3fbaa9fea4d90df',
    'нет$Кетчуп придумали в Англии в 19-м веке.$1540737/681b1fd4249e693ea529',

    'да$Плутон никогда полностью не совершал оборот вокруг Солнца$1540737/dfe9d510c91f15ee54d9',
    'да$В США больше библиотек, чем ресторанов Макдональдс.$937455/a38a3e0f2319b5fa7a7a',
    'да$Примерно на 60% клетки мозга состоят из жира$1652229/083e1999ccf25b806b2d',
    'нет$Меду нужно около 100 лет, чтобы испортиться$965417/709f7f212a4c119a9124'
]
cit='1652229/1e6a310f62b06b701c6d'
sessionStorage = {}

@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,
            'game_started': False
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            sessionStorage[user_id]['guessed_cities'] = []
            # Предлагаем ему сыграть и два варианта ответа "Да" и "Нет".
            res['response']['text'] = f'Приятно познакомиться, {first_name.title()}. Я Алиса. Давай поиграем в ~Правда или ложь~. Правила просты , если факт правдив ответь -"да" , иначе напиши - "нет" '
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                }
            ]
    else:
        if not sessionStorage[user_id]['game_started']:
            if 'да' in req['request']['nlu']['tokens']:
                if len(sessionStorage[user_id]['guessed_cities']) == 10:
                    res['response']['text'] = 'Молодец!'
                    res['response']['card'] = {}
                    res['response']['card']['type'] = 'BigImage'
                    res['response']['card']['title'] = 'Ты все прошел!!!'
                    res['response']['card']['image_id'] = cit
                    res['end_session'] = True
                else:

                    sessionStorage[user_id]['game_started'] = True
                    sessionStorage[user_id]['attempt'] = 1
                    play_game(res, req)
            elif 'нет' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Ну и ладно!'
                res['end_session'] = True
            else:
                res['response']['text'] = 'Не поняла ответа! Так да или нет?'
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    }
                ]
        else:
            play_game(res, req)


def play_game(res, req):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    if attempt == 1:
        city = random.choice(cities)
        while city in sessionStorage[user_id]['guessed_cities']:
            city = random.choice(cities)
        sessionStorage[user_id]['city'] = city
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = city.split('$')[1]
        res['response']['card']['image_id'] = city.split('$')[2]
        res['response']['text'] = 'Тогда сыграем!'
    else:
        a = ''
        city = sessionStorage[user_id]['city']
        a = get_info(req)
        if len(sessionStorage[user_id]['guessed_cities']) == 10:
            res['response']['text'] = 'Молодец'
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Ты все прошел!!!'
            res['response']['card']['image_id'] = cit
            res['end_session'] = True

        elif a == city.split('$')[0]:
            res['response']['text'] = 'Правильно! Продолжаем?'
            sessionStorage[user_id]['guessed_cities'].append(city)
            sessionStorage[user_id]['game_started'] = False
            return

        else:
            res['response']['text'] = 'Увы и ах, вы не правы. Продолжаем?'
            sessionStorage[user_id]['guessed_cities'].append(city)
            sessionStorage[user_id]['game_started'] = False
    sessionStorage[user_id]['attempt'] += 1


def get_info(req):
    cc = ''
    for entity in req['request']['nlu']['tokens']:
        cc+=str(entity)
        return cc


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name', то возвращаем её значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
