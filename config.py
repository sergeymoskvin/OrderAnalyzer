import os

# Базовые пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Имя выходного файла отчёта
OUTPUT_REPORT_FILENAME = 'summary_report.csv'

# Параметры фильтрации
STATUS_COLUMN = 'status'
STATUS_FILTER_VALUE = 'Delivered'

# Имена колонок с суммой и идентификатором заказа (для расчётов)
AMOUNT_COLUMN = 'total_amount'
ORDER_ID_COLUMN = 'order_id'

# Имя лог-файла
LOG_FILENAME = 'errors.log'