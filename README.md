#Rosebud BE - Django 3 / Python 3 reloaded

```
mkdir YourFolder
virtualenv -p python3 YourFolder
cd YourFolder
source bin/activate

pip install -r requirements.txt

./app.sh
```

Notes:
- For install *pycrypto* you need the python devel files:
  - Ubuntu 18: *sudo apt install python3-dev*
  - CentOS 7: *yum install python36u-devel*

- For install *mod_wsgi* you need the httpd devel files:
  - Ubuntu 18: *sudo apt install apache2-dev*
  - CentOS 7: *yum install httpd-devel*

- For install *mysql-client* you need the MySQL devel files:
  - Ubuntu 18: *sudo apt install default-libmysqlclient-dev*
  - CentOS 7: *yum install mysql-community-devel*


