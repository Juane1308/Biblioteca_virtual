from flask import Blueprint

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return "<h1>Biblioteca Virtual funcionando 📚</h1>"

