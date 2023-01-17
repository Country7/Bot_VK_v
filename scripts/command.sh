#!/usr/bin/env bash

pip freeze > requirements.txt

# запуск тестов в консоли
python -m unittest

# coverage
coverage run --source=bot,handlers,settings -m unittest
coverage report -m

# create PostgreSQL database
psql -U postgres -c "create database bot_vk"
psql -U postgres -d bot_vk
\dt
drop table userstate;
select * from userstate;
select * from registration;
