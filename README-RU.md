[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/+jJhUfsfFCn4zZDk0)      [![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/PAWSOG_bot/PAWS?startapp=uLnYLVgv)



## Recommendation before use

# 🔥🔥 PYTHON version must be 3.10 🔥🔥

> 🇪🇳 README in english available [here](README)

## Функционал  
|               Функционал               | Поддерживается |
|:--------------------------------------:|:--------------:|
|            Многопоточность             |       ✅        | 
|        Привязка прокси к сессии        |       ✅        | 
| Использование вашей реферальной ссылки |       ✅        |
|        Авто выполнение заданий         |       ✅        |
| Поддержка telethon И pyrogram .session |       ✅        |

_Скрипт осуществляет поиск файлов сессий в следующих папках:_
* /sessions
* /sessions/pyrogram
* /session/telethon

    PERFORM_TASKS: bool = True
    SUBSCRIPTIONS_PER_CYCLE: int = 1


## [Настройки](https://github.com/SP-l33t/Paws-Hybrid/tree/main/.env-example)
|          Настройки          |                                                                                                                              Описание                                                                                                                               |
|:---------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|    **API_ID / API_HASH**    |                                                                                         Данные платформы, с которой будет запущена сессия Telegram (по умолчанию - android)                                                                                         |
|   **GLOBAL_CONFIG_PATH**    | Определяет глобальный путь для accounts_config, proxies, sessions. <br/>Укажите абсолютный путь или используйте переменную окружения (по умолчанию - переменная окружения: **TG_FARM**)<br/> Если переменной окружения не существует, использует директорию скрипта |
|        **FIX_CERT**         |                                                                                              Попытаться исправить ошибку SSLCertVerificationError ( True / **False** )                                                                                              |
|    **TRACK_BOT_UPDATES**    |                                                                         Отслеживать обновления бота и останавливать бота, если были обновления, для проверки изменений ( **True** /False )                                                                          |
|         **REF_ID**          |                                                                                                Ваш реферальный идентификатор (В реферальной ссылке после startapp= )                                                                                                |
|      **PERFORM_TASKS**      |                                                                                                         Выполнять задания автоматически ( **True** / False)                                                                                                         |
|   **PERFORM_WALLET_TASK**   |                                                                                                     Выполнять задание с привязкой кошелька ( True / **False** )                                                                                                     |
|   **PERFORM_EMOJI_TASK**    |                                                                                                     Выполнять задание с добавлением emoji ( True / **False** )                                                                                                      |
| **SUBSCRIPTIONS_PER_CYCLE** |                                                                                          Количество заданий с подпиской на канал за круг. 0 = Подписки выключены ( **1** )                                                                                          |
|     **TWOCAPTCHA_API**      |                                                                                             https://2captcha.com/ API ключ для решения капчи для Activity Check задания                                                                                             |
|    **OVERWRITE_WALLETS**    |                                                                                 Переподключать кошельки, если подключенный и кошелёк в конфиг файле отличаются ( True / **False**)                                                                                  |
|   **CONNECT_WALLETS_WEB**   |                                                                           Подключать кошельки в приложении. Если в конфиге нет кошельков, они будут созданы автоматически (e.g. **True**)                                                                           |
|   **SESSION_START_DELAY**   |                                                                                           Случайная задержка при запуске. От 1 до указанного значения (например, **360**)                                                                                           |
|       **SLEEP_TIME**        |                                                                                                             Сон между итерациями ( **[43200, 86400]** )                                                                                                             |
|   **SESSIONS_PER_PROXY**    |                                                                                            Количество сессий, которые могут использовать один и тот же прокси ( **1** )                                                                                             |
|   **USE_PROXY_FROM_FILE**   |                                                                                             Использовать ли прокси из файла `bot/config/proxies.txt` (**True** / False)                                                                                             |
|  **DISABLE_PROXY_REPLACE**  |                                                                                   Отключить автоматическую проверку и замену нерабочих прокси перед стартом ( True / **False** )                                                                                    |
|      **DEVICE_PARAMS**      |                                                                                 Введите настройки устройства, чтобы телеграмм-сессия выглядела более реалистично (True / **False**)                                                                                 |
|      **DEBUG_LOGGING**      |                                                                                                Включить логирование трейсбэков ошибок в лог файл (True / **False**)                                                                                                 |

## Быстрый старт 📚

Для быстрой установки и последующего запуска - запустите файл run.bat на Windows или run.sh на Unix

## Предварительные условия
Прежде чем начать, убедитесь, что у вас установлено следующее:
- [Python](https://www.python.org/downloads/) **версии 3.10**

## Получение API ключей
1. Перейдите на сайт [my.telegram.org](https://my.telegram.org) и войдите в систему, используя свой номер телефона.
2. Выберите **"API development tools"** и заполните форму для регистрации нового приложения.
3. Запишите `API_ID` и `API_HASH` в файле `.env`, предоставленные после регистрации вашего приложения.

## Установка
Вы можете скачать [**Репозиторий**](https://github.com/SP-l33t/Paws-Hybrid) клонированием на вашу систему и установкой необходимых зависимостей:
```shell
git clone https://github.com/SP-l33t/Paws-Hybrid.git
cd Paws-Hybrid
```

Затем для автоматической установки введите:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux ручная установка
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Здесь вы обязательно должны указать ваши API_ID и API_HASH , остальное берется по умолчанию
python3 main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/Paws-Hybrid >>> python3 main.py --action (1/2)
# Or
~/Paws-Hybrid >>> python3 main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```


# Windows ручная установка
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Указываете ваши API_ID и API_HASH, остальное берется по умолчанию
python main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/Paws-Hybrid >>> python main.py --action (1/2)
# Или
~/Paws-Hybrid >>> python main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```
