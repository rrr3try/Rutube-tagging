Используемые библиотеки в requirements.txt
pytorch cuda 12.4

## генерация фичей обработка данных, аугментация
[model-run ](https://github.com/rrr3try/Rutube-tagging/blob/main/ed/model-run.ipynb)

1) Импорт модулей. Загрузка предоубученных моделей. XClip, ViVit, Whisper-v3, RuBert 
2) Генерация embeddings для Видео, Аудио и для текста
3) Сохранение в файл для обучения финального классификатора

## обучение мультиклассового классификатора
[prediction-pipeline](https://github.com/rrr3try/Rutube-tagging/blob/main/ed/model-run.ipynb)

1) Загрузка файлов эмбэддингов (сохранены на диск в предыдущем ноутбуке)
2) Препроцессинг, подбор гиперпараметров
3) Тестирование разных моделей machine learning для классификации, кросс-валидация




## 
