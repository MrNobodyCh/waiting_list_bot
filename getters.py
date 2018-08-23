# -*- coding: utf-8 -*-
import sys
import json

import psycopg2
import requests

from config import YClientsSetting

reload(sys)
sys.setdefaultencoding('utf-8')


class YClientsGetter(object):
    def __init__(self):
        self.login = YClientsSetting.LOGIN
        self.password = YClientsSetting.PASSWORD
        self.company_id = YClientsSetting.COMPANY_ID
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(YClientsSetting.BEARER_CODE)
        }
        self.headers_token = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}, User {}".format(YClientsSetting.BEARER_CODE, YClientsSetting.USER_TOKEN)
        }

    def auth_user(self):
        payload = {
            "login": self.login,
            "password": self.password
        }
        response = requests.post(url=YClientsSetting.AUTH_URL, data=json.dumps(payload), headers=self.headers)
        res = json.loads(response.text)

        if isinstance(res, dict) and res.get('errors'):
            return False, res.get('errors', {}).get('message', '')
        return True, ''

    def get_staff_info(self, staff_id):
        """Get info about specific staff"""
        response = requests.get(url=YClientsSetting.STAFF_URL + str(staff_id), headers=self.headers)
        return json.loads(response.text)

    def get_all_staff(self):
        """Get info about all staff"""
        response = requests.get(url=YClientsSetting.STAFF_URL, headers=self.headers)
        return json.loads(response.text)

    def get_records(self, staff_id=None, start_date=None, end_date=None):
        querystring = {"staff_id": int(staff_id)} if staff_id else {}
        querystring.update({"start_date": start_date} if start_date else {})
        querystring.update({"end_date": end_date} if end_date else {})
        response = requests.get(url=YClientsSetting.RECORDS_URL, params=querystring, headers=self.headers_token)
        return json.loads(response.text)

    def get_clients(self, phone=None):
        querystring = {"phone": str(phone)} if phone else {}
        response = requests.get(url=YClientsSetting.GET_CLIENTS, params=querystring, headers=self.headers_token)
        return json.loads(response.text)

    def get_specific_record(self, record_id):
        response = requests.get(url=YClientsSetting.SPECIFIC_RECORD_URL + str(record_id), headers=self.headers_token)
        return json.loads(response.text)

    def get_services(self):
        """Get info about services"""
        response = requests.get(url=YClientsSetting.SERVICES_URL, headers=self.headers)
        return json.loads(response.text)

    def get_specific_service(self, service_id):
        """Get info about specific service"""
        response = requests.get(url=YClientsSetting.SERVICES_URL + str(service_id), headers=self.headers)
        return json.loads(response.text)

    def get_services_by_category_and_staff(self, staff_id, category_id):
        response = requests.get(url=YClientsSetting.SERVICES_URL +
                                "service_id?staff_id=%s&category_id=%s" % (str(staff_id), str(category_id)),
                                headers=self.headers)
        return json.loads(response.text)

    def get_goods(self):
        """Get info about goods"""
        response = requests.get(url=YClientsSetting.GOODS_URL, headers=self.headers_token)
        return json.loads(response.text)

    def get_specific_good(self, good_id):
        """Get info about specific good"""
        response = requests.get(url=YClientsSetting.GOODS_URL + str(good_id), headers=self.headers_token)
        return json.loads(response.text)

    def change_record(self, record_id, staff_id, services, client,
                      datetime, seance_length, comment, attendance):
        payload = {
            "staff_id": staff_id,
            "services": services,
            "client": client,
            "datetime": datetime,
            "seance_length": seance_length,
            "save_if_busy": True,
            "send_sms": True,
            "attendance": attendance,  # 1 - Клиент пришел, услуги оказаны, -1 - Клиент не пришел
            "comment": comment
        }
        response = requests.put(url=YClientsSetting.CHANGE_RECORD_URL + str(record_id),
                                data=json.dumps(payload), headers=self.headers_token)
        return json.loads(response.text)

    def get_specific_visit(self, visit_id):
        """Get info about specific visit"""
        response = requests.get(url=YClientsSetting.GET_SPECIFIC_VISIT + str(visit_id), headers=self.headers_token)
        return json.loads(response.text)

    def change_visit(self, record_id, visit_id, goods_transactions, comment):
        payload = {
            "goods_transactions": goods_transactions,
            "attendance": 1,  # 1 - Пользователь пришел, услуги оказаны
            "comment": comment
        }
        response = requests.put(url=YClientsSetting.CHANGE_VISIT_URL + str(visit_id) + '/' + str(record_id),
                                data=json.dumps(payload), headers=self.headers_token)
        return json.loads(response.text)

    def get_storages(self):
        response = requests.get(url=YClientsSetting.STORAGES_URL, headers=self.headers_token)
        return json.loads(response.text)

    def get_service_categories(self):
        response = requests.get(url=YClientsSetting.SERVICE_CATEGORIES, headers=self.headers)
        return json.loads(response.text)

    def get_service_categories_by_staff(self, staff_id):
        response = requests.get(url=YClientsSetting.SERVICE_CATEGORIES + 'id?staff_id=%s' % staff_id,
                                headers=self.headers)
        print response.url
        return json.loads(response.text)


class DBGetter(object):
    def __init__(self, dbname):
        self.connection = psycopg2.connect(dbname=dbname)
        self.cur = self.connection.cursor()

    def insert(self, execution, values=None):
        self.cur.execute(execution, values)
        self.connection.commit()
        self.cur.close()
        self.connection.close()

    def get(self, execution):
        self.cur.execute(execution)
        rows = self.cur.fetchall()
        self.cur.close()
        self.connection.close()
        return rows
