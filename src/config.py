
class Local(object):
    """
    Development environment configuration
    """

    DEBUG = True
    TESTING = False
    PROJECT_ID = "yas-dev-tpm"
    SQLALCHEMY_DATABASE_URI = "mssql+pymssql://master:peacesells@DESKTOP-FGFDBVD\\TEW_SQLEXPRESS/avsInventory"


app_config = {
    "local":Local
}
