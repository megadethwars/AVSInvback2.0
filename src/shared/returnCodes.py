from flask import Response, json
from fastapi.responses import JSONResponse

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

def custom_response(res, status_code, app_code, message="", item=[],isQuery=False,total=0):
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


    if isQuery:
        response = {
            "app_code": app_code,
            "message": messageSent,
            "data": res,
            "total_rows":total
        }
    else:
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


def fastapi_response(res, status_code, app_code, message="", items=[], isQuery=False, total=0):
    """
    FastAPI Custom Response Function (returns JSONResponse)
    Compatible with legacy API contract
    
    Args:
        res: Response data
        status_code: HTTP status code
        app_code: TPM code (e.g., "TPM-1", "TPM-5")
        message: Custom message or empty for default
        items: List of error/object dicts from partial_response() or additional data
        isQuery: Include total_rows in response
        total: Total rows for query responses
    """
    messageSent = list()
    if message == "":
        messageSent.append({"status": app_codes[app_code]})
    else:
        messageSent.append({"status": str(message)})
    
    if isinstance(items, list):
        for x in items:
            messageSent.append(x)
    elif items != "":
        messageSent.append({"object": items})

    if isQuery:
        response = {
            "app_code": app_code,
            "message": messageSent,
            "data": res,
            "total_rows": total
        }
    else:
        response = {
            "app_code": app_code,
            "message": messageSent,
            "data": res,
        }
    
    return JSONResponse(status_code=status_code, content=response)
