from src.analyzer import OrderAnalyzer
from config import OUTPUT_REPORT_FILENAME


def main():
    analyzer = OrderAnalyzer()
    success, errors = analyzer.process_all_files()

    print(f"Обработано файлов успешно: {success}")
    print(f"Файлов с ошибками: {errors}")

    if success > 0:
        analyzer.save_report(OUTPUT_REPORT_FILENAME)
        print(f"Отчёт сохранён в папку reports/{OUTPUT_REPORT_FILENAME}")
    else:
        print("Ни одного файла не обработано — отчёт не создан.")


if __name__ == "__main__":
    main()