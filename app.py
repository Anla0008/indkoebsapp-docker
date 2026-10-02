from flask import Flask, request, jsonify

import x

app = Flask(__name__, static_folder="public", static_url_path="")


#######################################################################################
#                                      FORSIDE                                        #
#######################################################################################

# GET FORSIDE
############################################################
@app.get("/")
def index():
    return app.send_static_file("index.html")


#######################################################################################
#                                   INDKØBSLISTE                                      #
#######################################################################################

# GET VARER
############################################################
@app.get("/api/items")
def list_items():
    try:
        # Åbn en forbindelse til databasen og få en cursor til SQL.
        db, cursor = x.db()

        q = "SELECT id, name, quantity, is_bought FROM items ORDER BY id"
        cursor.execute(q)
        items = cursor.fetchall()

        return jsonify(items), 200

    except Exception as ex:
        # Fejlen vises i serverens terminal, ikke som databaseoplysninger i browseren.
        app.logger.exception("Kunne ikke hente varer: %s", ex)
        return jsonify(error="Kunne ikke hente varerne. Kontrollér databaseforbindelsen."), 500

    finally:
        # finally kører også, hvis vi allerede har sendt et svar med return.
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


# POST VARE
############################################################
@app.post("/api/items")
def create_item():
    try:
        # Hent og validér data, som JavaScript sender fra browseren.
        data = x.validate_json(request.get_json(silent=True))
        name = x.validate_item_name(data)
        quantity = x.validate_item_quantity(data)

        db, cursor = x.db()

        # %s er pladsholdere. Værdierne sendes separat for at undgå SQL injection.
        q = "INSERT INTO items (name, quantity) VALUES (%s, %s)"
        cursor.execute(q, (name, quantity))
        item_id = cursor.lastrowid

        # commit gemmer ændringen permanent i databasen.
        db.commit()

        return jsonify(id=item_id, name=name, quantity=quantity, is_bought=False), 201

    except ValueError as ex:
        # 400 betyder, at de indsendte data ikke er gyldige.
        return jsonify(error=str(ex)), 400

    except Exception as ex:
        if "db" in locals(): db.rollback()
        app.logger.exception("Kunne ikke oprette vare: %s", ex)
        return jsonify(error="Kunne ikke gemme varen. Prøv igen."), 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


# PATCH VARE – MARKER SOM KØBT ELLER IKKE KØBT
############################################################
@app.patch("/api/items/<int:item_id>")
def update_item(item_id):
    try:
        data = x.validate_json(request.get_json(silent=True))
        is_bought = x.validate_item_is_bought(data)

        db, cursor = x.db()

        # Tjek, at varen findes. Samme status kan godt sendes mere end én gang.
        q = "SELECT id FROM items WHERE id = %s"
        cursor.execute(q, (item_id,))
        item = cursor.fetchone()

        if not item:
            return jsonify(error="Varen findes ikke."), 404

        q = "UPDATE items SET is_bought = %s WHERE id = %s"
        cursor.execute(q, (is_bought, item_id))
        db.commit()

        return jsonify(id=item_id, is_bought=is_bought), 200

    except ValueError as ex:
        return jsonify(error=str(ex)), 400

    except Exception as ex:
        if "db" in locals(): db.rollback()
        app.logger.exception("Kunne ikke ændre vare: %s", ex)
        return jsonify(error="Kunne ikke ændre varen. Prøv igen."), 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


# DELETE VARE
############################################################
@app.delete("/api/items/<int:item_id>")
def delete_item(item_id):
    try:
        db, cursor = x.db()

        q = "DELETE FROM items WHERE id = %s"
        cursor.execute(q, (item_id,))

        if cursor.rowcount == 0:
            return jsonify(error="Varen findes ikke."), 404

        db.commit()

        # 204 betyder succes uden indhold. Din JavaScript håndterer allerede dette.
        return "", 204

    except Exception as ex:
        if "db" in locals(): db.rollback()
        app.logger.exception("Kunne ikke slette vare: %s", ex)
        return jsonify(error="Kunne ikke slette varen. Prøv igen."), 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


#######################################################################################
#                                    START SERVER                                     #
#######################################################################################

if __name__ == "__main__":
    # Lokal udviklingsserver. Dockeropsætningen kan senere bruge en anden startkommando.
    app.run(host="127.0.0.1", port=5000, debug=True)
