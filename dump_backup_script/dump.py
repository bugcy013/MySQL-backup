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

    def recent_full_backup_file(self):
        # Return last full backup dir name

        if len(os.listdir(self.full_dir)) > 0:
            return max(os.listdir(self.full_dir))
        else:
            return False


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
            return True
        else:
            return False


    def clean_full_backup_dir(self):
        # Deleting full backup after taking new full backup

        for i in os.listdir(self.full_dir):
            rm_dir = self.full_dir + '/' + i
            if i != max(os.listdir(self.full_dir)):
                shutil.rmtree(rm_dir)


    def take_dump_backup(self):

        # Defining file name based on datetime
        now = datetime.now().replace(second=0, microsecond=0)
        date = now[:10] + '_' + now[11:16]
        file_name = date

        # Taking Full backup
        command = '%s %s > %s/%s.sql' % (self.backup_tool, self.myuseroption, self.full_dir,file_name)
        args = shlex.split(command)
        fb = subprocess.Popen(args, stdout=subprocess.PIPE)
        print(str(fb.stdout.read()))