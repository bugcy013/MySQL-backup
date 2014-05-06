MySQL-backup
============

MySQL Backup and Prepare script written in Python 3.

Original Developers: Shahriyar Rzayev and Jahangir Shabiyev.
For community from Azerbaijan MySQL User Community: http://mysql.az/about/
For any question please ask: rzayev.sehriyar@gmail.com

===========

Requirements:

    * Percona Xtrabackup (latest version)
    * Python 3 (tested version 3.3.2)
    * Official mysql-connector-python (tested version 1.1.6)

===========

Script Logic:
    
    Xtrabackup is powerfull and open-source hot online backup tool  for MySQL from Percona.
    This script is using Xtrabackup for full and incremental backups.
    There will be 3 directory in tree (default location is /home):
        
        * backup_dir
        * backup_script
        * backup_prepare
    
    backup_dir -- is where your full and incremental backups will reside.
    backup_script -- is where backuper.py or backup script will reside.
    backup_prepare -- is where prepare scipt resides. After taking backup you must prepare it for recovery. This script will do it automatically.
    

