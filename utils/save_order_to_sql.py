import os
import json
from config_data.config import BRANCH_PHOTO, CUR, CONNECT_BASE, lock
from utils import plate_number_form


def list_orders():
    """
    Проверка всех папок в директории с заказ нарядами. При обнаружени файла с данными переностятся данные в SQL.
    После чего, по SQL бале проверяются всезаказ наряда на наличии папок, тех папок, что нет,
    в SQL ставиться признак закрытого заказ наряда
    Так же, проводится проверка наличия папок с номерами заказ нарадов с базой SQL при отсутствии папки SQL ставится
    призак закрытого заказ наряда
    :return:
    """
    list_orders_dict = []

    for item in os.listdir(BRANCH_PHOTO):
        new_way = os.path.join(BRANCH_PHOTO, item)
        if os.path.isdir(new_way):
            file_name = os.path.join(new_way, 'content 2.txt')
            if os.path.isfile(file_name):
                with open(file_name, 'r', encoding='utf-8') as file_open:
                    data = json.load(file_open)
                list_orders_dict.append(data)

    for item in list_orders_dict:
        with lock:
            data = (item['order'],)
            CUR.execute("""SELECT "order" FROM orders_list WHERE "order" = ? """, data)
        if CUR.fetchone():
            with lock:
                data_for_update = (item['barcode'],
                                   plate_number_form.read(item['plate_number']), item['phone'], item['order'], )
                CUR.execute("""UPDATE orders_list 
                SET barcode = ?, 
                    plate_number = ?, 
                    phone = ? 
                    WHERE "order" = ? """, data_for_update)
                CONNECT_BASE.commit()
        else:
            with lock:
                CUR.execute("""INSERT INTO "orders_list"("closed", "order", "phone", "plate_number", "barcode")
                                VALUES (FALSE, ?,?,?,?)""",
                                (item['order'], item['phone'],
                                 plate_number_form.read(item['plate_number']), item['barcode'], ))
                CONNECT_BASE.commit()

    orders_list = []
# Перевод статуса заказ нарада в архив

    for item in list_orders_dict:
        orders_list.append(item['order'])

    with lock:
        CUR.execute("""SELECT "order" FROM "orders_list" WHERE "closed" = FALSE""")
        orders_list_sql = CUR.fetchall()

    for item in orders_list_sql:
        order = item[0]
        if order not in orders_list:
            with lock:
                CUR.execute("""UPDATE orders_list SET closed = TRUE WHERE "order" = ?""", (order,))
                CONNECT_BASE.commit()
