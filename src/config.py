
class Local(object):
    """
    Development environment configuration
    """

    DEBUG = True
    version="1.0.0"
    TESTING = False
    PROJECT_ID = "yas-dev-tpm"
    SQLALCHEMY_DATABASE_URI = "mssql+pymssql://forrerunner97:Asterisco97@inventarioavs1.database.windows.net/avsInventory"
    JWT_SECRET_KEY = 'your-secret-key-change-this-in-production'  # Cambia esto por una clave secreta fuerte
    JWT_ACCESS_TOKEN_EXPIRES = False  # Los tokens no expiran (puedes configurar un tiempo si prefieres)


app_config = {
    "local":Local
}
