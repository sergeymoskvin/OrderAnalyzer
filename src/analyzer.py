import os
import logging
import pandas as pd
from config import (DATA_DIR, REPORTS_DIR, LOGS_DIR,
                    STATUS_COLUMN, STATUS_FILTER_VALUE,
                    AMOUNT_COLUMN, ORDER_ID_COLUMN,
                    LOG_FILENAME)


class OrderAnalyzer:
    """Класс для пакетного анализа CSV-файлов с заказами."""

    def __init__(self, data_dir: str = DATA_DIR,
                 reports_dir: str = REPORTS_DIR,
                 logs_dir: str = LOGS_DIR):
        self.data_dir = data_dir
        self.reports_dir = reports_dir
        self.logs_dir = logs_dir

        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

        log_file = os.path.join(self.logs_dir, LOG_FILENAME)
        logging.basicConfig(
            filename=log_file,
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        self.results = []

    def load_csv(self, filepath: str) -> pd.DataFrame:
        """Загружает CSV и проверяет корректность структуры и данных."""
        try:
            df = pd.read_csv(filepath)

            if df.empty:
                raise ValueError("Файл пуст")

            required_cols = {STATUS_COLUMN, AMOUNT_COLUMN, ORDER_ID_COLUMN}
            if not required_cols.issubset(df.columns):
                missing = required_cols - set(df.columns)
                raise ValueError(f"Отсутствуют обязательные колонки: {missing}")

            # Проверка, что total_amount числовой (если нет – ошибка)
            # Попытка преобразовать в число, нечисловые станут NaN
            numeric_amount = pd.to_numeric(df[AMOUNT_COLUMN], errors='coerce')
            if numeric_amount.isna().any():
                raise ValueError(f"Колонка {AMOUNT_COLUMN} содержит нечисловые значения")

            # Присваиваем обработанную колонку (на всякий случай)
            df[AMOUNT_COLUMN] = numeric_amount
            return df

        except Exception as e:
            self.logger.error(f"Ошибка при загрузке файла {filepath}: {e}")
            return None

    def filter_delivered(self, df: pd.DataFrame) -> pd.DataFrame:
        """Оставляет только заказы со статусом Delivered."""
        return df[df[STATUS_COLUMN] == STATUS_FILTER_VALUE]

    def calculate_metrics(self, df: pd.DataFrame) -> dict:
        """Рассчитывает метрики по доставленным заказам."""
        total_revenue = df[AMOUNT_COLUMN].sum()
        order_count = len(df)
        average_check = df[AMOUNT_COLUMN].mean() if order_count > 0 else 0.0

        return {
            'total_revenue': round(total_revenue, 2),
            'average_check': round(average_check, 2),
            'order_count': order_count
        }

    def process_file(self, filename: str) -> dict or None:
        """Полный цикл обработки одного файла с перехватом любых ошибок."""
        filepath = os.path.join(self.data_dir, filename)
        try:
            df = self.load_csv(filepath)
            if df is None:
                return None

            delivered_df = self.filter_delivered(df)
            metrics = self.calculate_metrics(delivered_df)
            metrics['filename'] = filename
            return metrics

        except Exception as e:
            self.logger.error(f"Ошибка при обработке файла {filepath}: {e}")
            return None

    def process_all_files(self) -> tuple[int, int]:
        """Обрабатывает все CSV-файлы в data_dir, возвращает (успех, ошибки)."""
        if not os.path.isdir(self.data_dir):
            self.logger.error(f"Папка с данными не найдена: {self.data_dir}")
            return 0, 0

        all_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        success_count = 0
        error_count = 0

        for file in all_files:
            result = self.process_file(file)
            if result is not None:
                self.results.append(result)
                success_count += 1
            else:
                error_count += 1

        return success_count, error_count

    def save_report(self, report_filename: str) -> None:
        """Сохраняет накопленные метрики в CSV-отчёт."""
        if not self.results:
            self.logger.warning("Нет данных для сохранения отчёта")
            return

        df_report = pd.DataFrame(self.results)
        df_report = df_report[['filename', 'total_revenue', 'average_check', 'order_count']]
        report_path = os.path.join(self.reports_dir, report_filename)
