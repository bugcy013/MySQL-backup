import configparser
import subprocess
import shlex
import os
import datetime
import shutil
from datetime import datetime


class MysqlDumper:
    """

    Class for using mysqldump utility.

    """

    def __init__(self, conf='/home/dump_backup_script/bck.conf'):

        con = configparser.ConfigParser()
        con.read(conf)
        bolme = con.sections()

        DB = bolme[0]
        self.mysql = con[DB]['mysql']
        self.mycnf = con[DB]['mycnf']
        self.myuseroption = con[DB]['useroption']


        BCK = bolme[1]
        self.backupdir = con[BCK]['backupdir']
        self.full_dir = self.backupdir + '/dumps'
        self.backup_tool = con[BCK]['backup_tool']

        if not (os.path.exists(self.full_dir)):
            print('Full directory is not exist. Creating full backup directory...')
            os.makedirs(self.backupdir + '/dumps')
            print('Created')


    def clean_full_backup_dir(self):
        # Deleting full backup after taking new full backup

        for i in os.listdir(self.full_dir):
            rm_dir = self.full_dir + '/' + i
            if i != max(os.listdir(self.full_dir)):
                shutil.rmtree(rm_dir)


    def take_dump_backup(self):

        # Defining file name based on datetime
        now = datetime.now().replace(second=0, microsecond=0)
        now = str(now)
        date1 = now[:10] + '_' + now[11:16]
        file_name = date1

        # Taking Full backup
        command = '%s %s > %s/%s.sql' % (self.backup_tool, self.myuseroption, self.full_dir, file_name)
        # args = shlex.split(command)
        # fb = subprocess.Popen(args, stdout=subprocess.PIPE)
        # print(str(fb.stdout.read()))

        print(command)


    def all_procedures(self):

        # Calling Backup function

        self.take_dump_backup()

        # Cleaning old backup

        self.clean_full_backup_dir()


x = MysqlDumper()
#x.all_procedures()
x.take_dump_backup()