"""Databaseforbindelse og validering til indkøbsappen."""
import os

import mysql.connector


#######################################################################################
#                               DATABASEFORBINDELSE                                   #
#######################################################################################

def db():
    try:
        db = mysql.connector.connect(
            host = "mariadb",
            user = "root",  
            password = "password",
            database = "to_do" # Navnet på den database vi har i vores docker (kan skiftes til docker-compose.ylm)
        )
        cursor = db.cursor(dictionary=True)
        return db, cursor
    except Exception as e:
        print(e, flush=True)
        raise Exception("Database under maintenance", 500)


#######################################################################################
#                                   VALIDERING                                        #
#######################################################################################

def validate_json(data):
    if not isinstance(data, dict):
        raise ValueError("Send data som et JSON objekt.")
    return data


def validate_item_name(data):
    name = data.get("name")
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 255:
        raise ValueError("Skriv et varenavn på højst 255 tegn.")
    return name.strip()


def validate_item_quantity(data):
    quantity = data.get("quantity")
    if type(quantity) is not int or not 1 <= quantity <= 9999:
        raise ValueError("Antal skal være et helt tal mellem 1 og 9999.")
    return quantity


def validate_item_is_bought(data):
    is_bought = data.get("is_bought")
    if type(is_bought) is not bool:
        raise ValueError("is_bought skal være true eller false.")
    return is_bought
