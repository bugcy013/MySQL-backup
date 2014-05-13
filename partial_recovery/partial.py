import mysql.connector
from mysql.connector import errorcode
import time
import configparser
import os

class PartialRecovery:

    def __init__(self, conf='bck.conf'):

        """
            Initialize function, which read bck.conf file from same directory
        """

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

    def get_table_ibd_file(self, database_name, table_name):
        """
            This function purpose to locate backed up database and table.
             Exactly we are looking for .ibd file.
             .ibd file is a tablespace where table data located.
        """


        database_dir_list = []
        database_dir_abspath = []
        table_dir_list = []


        # look for all files in database directory
        for i in os.listdir(self.full_dir):
            for x in os.listdir(self.full_dir+"/"+i):
                if os.path.isdir(self.full_dir+"/"+i+"/"+x) and x == database_name:
                    for z in os.listdir(self.full_dir+"/"+i+"/"+x):
                        database_dir_list.append(z)
                        path_name = os.path.abspath(z)
                        database_dir_abspath.append(path_name)

        # If database directory exists find already provided table in database directory
        if len(database_dir_list) > 0:
            for i in database_dir_list:
                base_file = os.path.splitext(i)[0]
                ext = os.path.splitext(i)[1]

                if table_name == base_file:
                    table_dir_list.append(i)


        # If table name from input is valid and it is located in database directory return .ibd file name
        if len(database_dir_list) > 0 and len(table_dir_list) == 2: # Why 2? because every table must have .frm and .ibd file
            for i in table_dir_list:
                base_file = os.path.splitext(i)[0]
                ext = os.path.splitext(i)[1]
                if ext == '.ibd':
                    print(i)
        else:
            print("There is no such Database or Table")

        for i in database_dir_abspath:
            print(i)


    def final_actions(self):
        # Type Database name of table which you want to restore
        database_name = input("Type Database name: ")

        # Type name of table which you want to restore
        table_name = input("Type Table name: ")

        self.get_table_ibd_file(database_name=database_name, table_name=table_name)


a = PartialRecovery()
#print(a.get_table_ibd_file())
a.final_actions()
