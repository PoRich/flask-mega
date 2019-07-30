from application import app
import click
import os


@app.cli.group()
def translate():
    ''' Translation and localization commands. '''
    pass


''' app.cli.group() decorator creates a roote (translate) for several
sub-commands; name of the commands comes from the decorated function; translate
only exists to provide a base for the sub commands '''


@translate.command()
def update():
    ''' Update all languages '''
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d application/translations'):
        raise RuntimeError('update command failed')
    os.remove('messages.pot')


''' for all commands, the functions run them, and makes sure the return value
is zero, which implies it did not return any errors. if the command errors,
then raise a RuntimeError'''


@translate.command()
def compile():
    ''' Compile all languages '''
    if os.system('pybabel compile -d application/translations'):
        raise RuntimeError('compile command failed')


@translate.command()
@click.argument('lang')
def init(lang):
    ''' Initialize a new language '''
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system(
            'pybabel init -i messages.pot -d application/translations -l ' +
            lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot)')
