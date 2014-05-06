#!/usr/bin/python3
# Backup script for MySQL DB (using the latest version of Xtrabackup)(tested with MySQL 5.6.12 on Ubuntu 12.04)
# Originally developed by Jahangir Shabiyev /
# Improved by Shahriyar Rzayev / rzayev.sehriyar@gmail.com
import os
import configparser
import subprocess
import shlex
import shutil
import mysql.connector
import time
from datetime import datetime
from mysql.connector import errorcode


# Creating Backup class

class Backup:
    def __init__(self, conf='/home/backup_script/bck.conf'):
        con = configparser.ConfigParser()
        con.read(conf)
        bolme = con.sections()
        DB = bolme[0]
        self.mysql = con[DB]['mysql']
        self.mycnf = con[DB]['mycnf']
        self.mysqladmin = con[DB]['mysqladmin']
        self.myuseroption = con[DB]['useroption']
        self.xtrabck = con[DB]['xtra']

        BCK = bolme[1]
        self.backupdir = con[BCK]['backupdir']
        self.full_dir = self.backupdir + '/full'
        self.inc_dir = self.backupdir + '/inc'
        self.backup_tool = con[BCK]['backup_tool']

        RM = bolme[2]
        self.remote_conn = con[RM]['remote_conn']
        self.remote_dir = con[RM]['remote_dir']

        statusargs = '%s %s status' % (self.mysqladmin, self.myuseroption)
        statusargs = shlex.split(statusargs)
        myadmin = subprocess.Popen(statusargs, stdout=subprocess.PIPE)
        if not ('Uptime' in str(myadmin.stdout.read())):
            print('Server is NOT Up')
        else:
            print('Server is Up')

        if not os.path.exists(self.mycnf):
            print('Check MySQL configuration file path')

        if not os.path.exists(self.mysql):
            print('Check MySQL')

        if not os.path.exists(self.mysqladmin):
            print('Check MySQL Admin')

        if not os.path.exists(self.backup_tool):
            print('Check backup tool')

        if not (os.path.exists(self.backupdir)):
            print('Check core backup directory')

        if not (os.path.exists(self.full_dir)):
            print('Full directory is not exist. Creating full backup directory...')
            os.makedirs(self.backupdir + '/full')
            print('Created')

        if not (os.path.exists(self.inc_dir)):
            print('Increment directory is not exist. Creating increment backup directory...')
            os.makedirs(self.backupdir + '/inc')
            print('Created')


    def last_full_backup_date(self):
        # Finding last full backup date from dir/folder name

        max = self.recent_full_backup_file()
        dir_date_str = max[:4] + '-' + max[5:7] + '-' + max[8:10] + ' ' + max[11:13] + ':' + max[14:16]
        dir_date = datetime.strptime(dir_date_str, "%Y-%m-%d %H:%M")
        now = datetime.now().replace(second=0, microsecond=0)

        # Defining variables for comparison.

        a = '2013-09-04 15:29'
        b = '2013-09-03 15:29'
        a = datetime.strptime(a, "%Y-%m-%d %H:%M")
        b = datetime.strptime(b, "%Y-%m-%d %H:%M")
        diff = a - b

        # Finding if last full backup is 1 day or more from now!

        if now - dir_date >= diff:
            return 1
        else:
            return 0


    def recent_full_backup_file(self):
        # Return last full backup dir name

        if len(os.listdir(self.full_dir)) > 0:
            return max(os.listdir(self.full_dir))
        else:
            return 0


    def mysql_connection_flush_logs(self):
        """
        It is highly recomended to flush binary logs before each full backup for easy maintenance.
        That's why we will execute "flush logs" command before each full backup!
        Also for security purposes you must create a MySQL user with only RELOAD privilege,
        It is sufficient for this backup script.
        I provide eg. create user statement:
        """
        # ############################################################
        # create user 'test_backup'@'127.0.0.1' identified by '12345';
        # grant all on bck.* to 'test_backup'@'127.0.0.1';
        # grant reload on *.* to 'test_backup'@'127.0.0.1';
        # ############################################################

        # Also create a test database for connection
        # create database bck;


        config = {

            'user': 'test_backup',
            'password': '12345',
            'host': '127.0.0.1',
            'database': 'bck',
            'raise_on_warnings': True,

        }

        # Open connection
        try:
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()
            query = "flush logs"
            print("Flushing Binary Logs")
            time.sleep(2)
            cursor.execute(query)
            cursor.close()
            cnx.close()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exists")
            else:
                print(err)





    def clean_full_backup_dir(self):
        # Deleting full backup after taking new full backup

        for i in os.listdir(self.full_dir):
            rm_dir = self.full_dir + '/' + i
            if i != max(os.listdir(self.full_dir)):
                shutil.rmtree(rm_dir)


    def clean_inc_backup_dir(self):
        # Deleting incremental backups after taking new fresh full backup

        for i in os.listdir(self.inc_dir):
            rm_dir = self.inc_dir + '/' + i
            shutil.rmtree(rm_dir)


    def copy_backup_to_remote_host(self):
        # Copying backup directory to remote server
        print("#################################################################################################")
        print("Copying backups to remote server")
        print("#################################################################################################")
        copy_it = 'scp -r %s %s:%s' % (self.backupdir, self.remote_conn, self.remote_dir)
        copy_it = shlex.split(copy_it)
        cp = subprocess.Popen(copy_it, stdout=subprocess.PIPE)
        print(str(cp.stdout.read()))


    def full_backup(self):
        # Taking Full backup

        args = '%s %s %s %s' % (self.backup_tool, self.myuseroption, self.xtrabck, self.full_dir)
        args = shlex.split(args)
        fb = subprocess.Popen(args, stdout=subprocess.PIPE)
        print(str(fb.stdout.read()))


    def inc_backup(self):
        # Taking Incremental backup

        recent_bck = self.recent_full_backup_file()
        args = '%s %s %s --incremental %s --incremental-basedir %s/%s' % (
            self.backup_tool, self.myuseroption, self.xtrabck, self.inc_dir, self.full_dir, recent_bck)
        args = shlex.split(args)
        ib = subprocess.Popen(args, stdout=subprocess.PIPE)
        print(str(ib.stdout.read()))


    def all_backup(self):
        """
         This function firstly checks for full backup directory if it is empty takes full backup.
         If it is not empty then checks for full backup time.if the recent full backup taken 1 day ago takes full backup
         Any other options it takes incremental backup
        """
        if self.recent_full_backup_file() == 0:
            print("################################################################")
            print("You have no backups : Taking very first Full Backup!")
            print("################################################################")

            time.sleep(3)

            # Flushing Logs
            self.mysql_connection_flush_logs()

            # Taking fullbackup
            self.full_backup()

            # Copying backups to remote server
            #self.copy_backup_to_remote_host()

        elif self.last_full_backup_date() == 1:
            print("################################################################")
            print("Your full backup is timeout : Taking new Full Backup!")
            print("################################################################")

            time.sleep(3)

            # Flushing logs
            self.mysql_connection_flush_logs()

            # Taking fullbackup
            self.full_backup()

            # Removing old full backups
            self.clean_full_backup_dir()

            # Removing inc backups
            self.clean_inc_backup_dir()

            # Copying backups to remote server
            #self.copy_backup_to_remote_host()

        else:
            print("################################################################")
            print("You have a full backup. "
                  "We will take an incremental one based on recent Full Backup")
            print("################################################################")

            time.sleep(3)

            # Taking incremental backup
            self.inc_backup()

            # Copying backups to remote server
            #self.copy_backup_to_remote_host()


b = Backup()
b.all_backup()
