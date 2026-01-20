import streamlit as st
import time
import re
import shutil
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

st.set_page_config(page_title="Monitor", layout="centered")

def get_rate():
    try:
        # 1. Настройки Хрома для сервера
        options = Options()
        options.add_argument("--headless=new") # Без окна
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # 2. Ищем пути к Хрому, который установил Railway
        chromium_path = shutil.which("chromium")
        chromedriver_path = shutil.which("chromedriver")
        
        if chromium_path:
            options.binary_location = chromium_path
            
        # 3. Запускаем драйвер
        if chromedriver_path:
            service = Service(executable_path=chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            # Запасной вариант (скачивание)
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

        driver.set_page_load_timeout(30)
        
        # 4. Заходим на сайт
        driver.get("https://www.profinance.ru/currency_eur.asp")
        time.sleep(3) # Ждем прогрузки
        html = driver.page_source
        driver.quit()

        # 5. Ищем цифры (Regex)
        patterns = [
            r'EUR/RUB[^\d]*(\d{2}[.,]\d{2,4})',
            r'EURRUB[^\d]*(\d{2}[.,]\d{2,4})',
            r'bid["\s:=]+(\d{2}[.,]\d{2,4})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                val = float(match.replace(',', '.'))
                if 80 < val < 150:
                    return val
        return None

    except Exception as e:
        st.error(f"Ошибка: {e}")
        return None

# === ИНТЕРФЕЙС ===
st.title("💶 Курс Profinance (Selenium)")

if st.button("Обновить курс", type="primary"):
    with st.spinner("Запускаю браузер на сервере..."):
        rate = get_rate()
        if rate:
            st.success(f"Текущий курс: {rate} ₽")
        else:
            st.error("Не удалось найти курс на странице")