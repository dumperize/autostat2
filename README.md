Запускаем docker-compose up -d --build

по адресу: 
http://127.0.0.1:8000/generate_dictionary GET
просим заново перегенерировать весь словарь с марками и моделями

http://127.0.0.1:8000/invacation_file POST
можно отправить файл в формате csv 
id,text
1,ДЖИП ГРАНД ЧИРОКИ2000 года выпуска
2,ДЖИП ГРАНД ЧИРОКИ2001 года выпуска

http://127.0.0.1:8000/invacation
можно отправить json в формате
[
{"id":"1", "text": "ДЖИП ГРАНД ЧИРОКИ2000 года выпуска"},
{"id":"2", "text": "ДЖИП ГРАНД ЧИРОКИ2001 года выпуска"},
]


Настроить порты адрес можно в файле docker-compose.yaml:

Также в разделе volumes можно указать свой путь до папки с файлом списка моделей и марок в первой части до двоеточия:
      - ./data:/code/data

Базовое регулярное выражение для нахождения года находится вот тут: data/year_regular.txt
Оно ограничено 2022 годом. Можно поменять последнюю цифру на 3, чтобы он начал захватывать 2023 год.