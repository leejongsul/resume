# -*- coding: utf-8 -*-
from math import floor

from sqlalchemy.exc import IntegrityError

from common_func import Bunch
from database_models import db
from database_models.AccountModel import Account
from database_models.ProductModel import Product
from database_models.VipModel import Vip
from mongo_models.LogModel import ErrorLog, SessionLog, AccountLog
from redis_models.AccountModel import RedisAccount
from redis_models.SessionModel import RedisSessions
from redis_models.redis_func import gen_session_id

__author__ = 'terry'


class AccountController:
    def __init__(self):
        self.response = None
        self.db = db
        self.session_id = None

    def set_account(self, account_id, account_name, account_profile, account_type, cellphone, device_type, device_id,
                    device_token, registration_id):
        # DB Account Register
        account = self.__db_save_account(account_id, account_name, account_profile, account_type, cellphone)
        if account is False:
            return False

        # Gen & Save Session id
        account.session_id = self.set_session(account_id)
        account.device_type = device_type
        account.device_id = device_id
        account.device_token = device_token
        account.registration_id = registration_id

        # Redis Register
        redis_save_result = self.__redis_save_account(account)
        if redis_save_result is False:
            return False

        # Write LOG
        try:
            AccountLog(account)
        except:
            message = u'계정 생성 로그를 저장하지 못했습니다.'
            ErrorLog(message)

        return account

    def update_profile(self, id, account_name, account_profile):
        redis_account = self.get_redis_account(id)
        data = {}

        if account_name and account_name != redis_account['account_name']:
            data['account_name'] = account_name
        if account_profile and account_profile != redis_account['account_profile']:
            data['account_profile'] = account_profile

        if len(data) > 0:
            try:
                self.db.session.query(Account).filter(Account.id == id).update(data)
                self.db.session.commit()
            except IntegrityError:
                self.db.session.rollback()
                self.db.session.flush()
                # Error log
                message = u'account_name duplicate'
                ErrorLog(message)
                return False

            for k in data:
                redis_account[k] = data[k]
            redis_save_result = self.__redis_save_account(redis_account)
            if redis_save_result is False:
                return False
            return self.get_redis_account(id)
        else:
            return redis_account

    def buy_jewel(self, redis_account, product_id):
        account = self.get_account_by_account_id(redis_account['account_id'])
        product = self.get_product_by_product_id(product_id)

        # TODO - In-App purchase 로직 추가해야함.

        # VIP 레벨에 따른 추가 혜택
        if 0 < account.vip_level < 15:
            vip_info = self.get_vip_by_vip_level(account.vip_level)
        elif account.vip_level == 0:
            vip_info = self.get_vip_by_vip_level(1)
        else:
            vip_info = self.get_vip_by_vip_level(15)

        bonus = product.obtain_bonus * (vip_info.bonus_rate / 100.0)
        # VIP 레벨업
        # TODO - $1 당 올라가는 VIP EXP(50)
        # TODO - VIP MAX LEVEL(15) 하드 코딩 제거.
        exp = floor(product.price) * 50
        account.vip_exp += exp
        if account.vip_level < 15 and vip_info.require_exp <= account.vip_exp:
            account.vip_level += 1
        account.jewel += (product.obtain_bonus + bonus)

        try:
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            self.db.session.flush()
            return False

        account.session_id = redis_account['session_id']
        redis_save_result = self.__redis_save_account(account)
        if redis_save_result is False:
            return False
        return self.get_redis_account(account.id)

    def buy_coin(self, redis_account, product_id):
        account = self.get_account_by_account_id(redis_account['account_id'])
        product = self.get_product_by_product_id(product_id)

        if product is None:
            return 1

        if account.jewel < product.price_jewel:
            return 2

        # VIP 레벨에 따른 추가 혜택
        # TODO - VIP MAX LEVEL(15) 하드 코딩 제거.
        if 0 < account.vip_level < 15:
            vip_info = self.get_vip_by_vip_level(account.vip_level)
        elif account.vip_level == 0:
            vip_info = self.get_vip_by_vip_level(1)
        else:
            vip_info = self.get_vip_by_vip_level(15)

        bonus = product.obtain_bonus * (vip_info.bonus_rate / 100.0)
        account.jewel -= product.price_jewel
        account.coin += (product.obtain_bonus + bonus)

        try:
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            self.db.session.flush()
            # out of range
            if e.orig[0] == 1264:
                return 3
            return False

        account.session_id = redis_account['session_id']
        redis_save_result = self.__redis_save_account(account)
        if redis_save_result is False:
            return False
        return self.get_redis_account(account.id)
