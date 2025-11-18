# config.py

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:Churro1234!@localhost/mechanic_db"
    DEBUG = True
    
class TestingConfig:
    pass

class ProductionConfig: 
    pass