from flask import Flask
from flask.ext.script import Manager
from flask.ext.script import Command
from app.app import App
import logging

app = App()
manager = Manager(app)

class RunWorker(Command):

    def run(self):
        logging.info("command!")


manager.add_command('command', RunWorker())
#python manager.py command

if __name__ == "__main__":
    manager.run()
