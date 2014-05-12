import mysql.connector
from mysql.connector import errorcode
import time
import configparser
import os

class PartialRecovery:

    def __init__(self, conf='bck.conf'):
        con = configparser.ConfigParser()
        con.read(conf)
        bolme = con.sections()

        DB = bolme[0]
        self.datadir = con[DB]['datadir']


        BCK = bolme[1]
        self.backupdir = con[BCK]['backupdir']
        self.full_dir = self.backupdir + '/full'
        self.inc_dir = self.backupdir + '/inc'


        CM = bolme[2]
        self.chown_command = con[CM]['chown_command']


    def get_mysql_connection(self):

        config = {

            'user': 'root',
            'password': '12345',
            'host': '127.0.0.1',
            'database': 'bck',
            'raise_on_warnings': True,

        }

        # Open connection
        try:
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()
            query="select 1 from dual"
            cursor.execute(query)
            for i in cursor:
                print(i)

            cursor.close()
            cnx.close()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exists")
            else:
                print(err)

    # def run_query(self):
    #     query="select 1 from dual"
    #     self.get_mysql_connection().execute(query)
    #     for i in self.get_mysql_connection():
    #         print(i)

    def backup_file_processes(self):
        for i in os.listdir(self.full_dir):
            print(i)




a = PartialRecovery()
a.get_mysql_connection()






