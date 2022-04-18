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
    "TPM-9": "Recurso eliminado exitosamente",
    "TPM-10": "Acceso no autorizado",
    "TPM-11": "El operador/supervisor no tiene permisos para realizar estas operaciones",
    "TPM-12": "Ocurrio algun error al crear el registro",
    "TPM-13": "Ocurrio un error durante la actualizacion de este objeto",
    "TPM-14": "Ocurrio un error al obtener algunos registros",
    "TPM-15": "Ocurrio un error al actualizar algunos registros",
    "TPM-16": "Ocurrio un error al crear algunos registros",
    "TPM-17":"No hay suficientes equipos para ejecutar salida",
    "TPM-18":"Acceso autorizado",
    "TPM-19":"Usuario dado de baja, error en inicio de sesion"
}


def partial_response(app_code,message="",name="",id=0):
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
