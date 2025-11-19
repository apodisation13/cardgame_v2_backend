import os
print(f"\n🔍 Loading conftest.py from: {os.path.abspath(__file__)}")

# # Переопределяем конфиг для тестов
# os.environ["CONFIG"] = "test_local"
# print("STR75 set config api")

from lib.tests.fixtures import *
from services.api.tests.fixtures import *
