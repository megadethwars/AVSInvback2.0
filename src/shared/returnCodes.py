from flask import Response, json

# Diccionario de return codes
app_codes = {
    "TPM-1": "Creado exitosamente",
    "TPM-2": "Error en la formación del json de entrada",
    "TPM-3": "Consulta exitosa",
    "TPM-4": "Recurso no encontrado",
    "TPM-5": "El recurso ya existe",
    "TPM-6": "Recurso actualizado correctamente",
    "TPM-7": "Error interno del servidor",
    "TPM-8": "Recursos creados exitosamente",
    "TPM-9": "La cuenta se ha validado correctamente",
    "TPM-10": "El beneficiario de la cuenta no coincide con el nombre del comisionista",
    "TPM-11": "No se pudo crear el lego de persona en la BUP",
    "TPM-12": "Se requieren al menos los datos mínimos para poder crear la persona en la BUP",
    "TPM-13": "Ocurrió un error al crear el registro en el lego de datos mínimos en la BUP",
    "TPM-14": "Ocurrió un error al crear el registro en el lego de datos mínimos persona moral en la BUP",
    "TPM-15": "Ocurrió un error al crear el registro en el lego de datos básicos en la BUP",
    "TPM-16": "Ocurrió un error al crear el registro en el lego de datos básicos persona moral en la BUP",
    "TPM-17": "Ocurrió un error al crear el registro en el lego de datos de contacto en la BUP",
    "TPM-18": "Ocurrió un error al crear el registro en el lego de datos complemento yastás en la BUP",
    "TPM-19": "No se pudo crear ningún registro",
    "TPM-20": "Algunos registros no se pudieron crear"
}


def partial_response(app_code,message="",name="",id=""):
    if message=="":
        message = app_codes[app_code]
    
    return {
            app_code:app_code,
            "message":message,
            "errors":name,
            "id":id
            }

def custom_response(res, status_code, app_code, message="", item=[]):
    """
    Custom Response Function
    """
    messageSent = list()
    if message == "":
        messageSent.append({"status":app_codes[app_code]})
    else:
        messageSent.append({"status":str(message)})
    
    if type(item) == list:
        for x in item:
            messageSent.append(x)
    else:
        messageSent.append({"object":item})       

    response = {
        "app_code": app_code,
        "message": messageSent,
        "data": res,
    }
    return Response(
        mimetype="application/json",
        response=json.dumps(response),
        status=status_code,
    )
