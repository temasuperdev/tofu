from flasgger import Swagger

def configure_swagger(app):
    """
    Настройка Swagger документации для Flask приложения
    """
    app.config['SWAGGER'] = {
        'title': 'Demo App API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'API documentation for the K3s Demo Application',
        'termsOfService': '',
        'contact': {
            'name': 'API Support',
            'email': 'support@example.com',
        },
        'license': {
            'name': 'MIT',
            'url': 'http://mit-license.org/',
        },
    }

    swagger = Swagger(app, template={
        'info': {
            'title': 'Demo App API',
            'version': '1.0.0',
            'description': 'API documentation for the K3s Demo Application',
        },
        'consumes': [
            'application/json',
        ],
        'produces': [
            'application/json',
        ],
    })

    return swagger