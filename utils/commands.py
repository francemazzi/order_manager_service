import click
from flask.cli import with_appcontext
from models.user import User
from extensions import db

@click.command('list-users')
@with_appcontext
def list_users():
    users = User.query.all()
    for user in users:
        click.echo(f'User: {user.email}')

@click.command('shell')
@with_appcontext
def shell_command():
    import code
    code.interact(local=locals()) 