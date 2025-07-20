
class Local(object):
    """
    Development environment configuration
    """

    DEBUG = True
    version="1.0.0"
    TESTING = False
    PROJECT_ID = "yas-dev-tpm"
    SQLALCHEMY_DATABASE_URI = "mssql+pymssql://forrerunner97:Asterisco97@inventarioavs1.database.windows.net/avsInventory"


app_config = {
    "local":Local
}
