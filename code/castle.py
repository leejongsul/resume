import logging
from exceptions.signalnco_exception import SignalncoException

import aiohttp.web

import utils.time
from dao.purchases_dao import PurchasesDao
from services.purchase.apple import AppleService
from services.purchase.google_developer_api import GoogleDeveloperAPIService


class PlatformType:
    def __init__(self):
        pass

    ANDROID = 1
    IOS = 2


class PurchaseService:
    def __init__(self):
        pass

    async def validate(self):
        pass

    async def _save(self):
        pass

    @staticmethod
    def get_instance(app, platform_type):
        if platform_type == PlatformType.ANDROID:
            return GooglePurchaseService(app)
        elif platform_type == PlatformType.IOS:
            return ApplePurchaseService(app)
        else:
            raise SignalncoException("not supported platform.", 400)

    async def check_session_key(self, session, random_key):
        # session의 random_key와 request payload의 random_key 검증
        if random_key != session['random_key']:
            logging.info("random_key is invalid")
            result = {
                'result': 'invalid developerPayload',
                'code': 400
            }
            return aiohttp.web.json_response(result,
                                             status=result['code'])
        else:
            logging.info("random_key is valid")
            return None


class GooglePurchaseService(PurchaseService):
    def __init__(self, app):
        self.app = app

    async def validate(self, payload, session):
        logging.debug("AOS payload: {}".format(payload))
        random_key = payload['developerPayload']
        await self.check_session_key(session, random_key)

        api_result = await self._validate(payload)
        if 'succeed' in api_result and api_result['succeed'] is True:
            await self._save(api_result['data'])
            return {
                'result': 'succeed',
                'code': 200
            }
        else:
            return {
                'result': 'verify failed',
                'code': 400
            }

    async def _validate(self, payload):
        package_name = payload['packageName']
        product_id = payload['productId']
        purchase_token = payload['purchaseToken']

        logging.info("packageName={}, productId={}, purchaseToken={}".format(
            package_name,
            product_id,
            purchase_token))

        googl_api_service = GoogleDeveloperAPIService(
            self.app,
            package_name,
            product_id,
            purchase_token)

        return await googl_api_service.validate()

    async def _save(self, result):
        # 영수증 DB 저장
        purchases_dao = PurchasesDao(self.app['db'])
        dt = await utils.time.ms_timestamp_to_datetime(
            result['purchaseTimeMillis'])
        return await purchases_dao.create(
            platform_type=PlatformType.ANDROID,
            order_id=result['orderId'],
            product_id=result['productId'],
            purchase_at=dt)


class ApplePurchaseService(PurchaseService):
    def __init__(self, app):
        self.app = app

    async def validate(self, payload, session):
        logging.debug("iOS payload: {}".format(payload))
        random_key = payload['developerPayload']
        await self.check_session_key(session, random_key)
        apple_service = AppleService(self.app)
        api_result = await apple_service.validate(payload['Payload'])
        if 'succeed' in api_result and api_result['succeed'] is True:
            await self._save(api_result['data']['receipt']['in_app'][0])
            return {
                'result': 'succeed',
                'code': 200
            }
        else:
            return {
                'result': 'verify failed',
                'code': 400
            }

    async def _save(self, receipt_data):
        # 영수증 DB 저장
        purchases_dao = PurchasesDao(self.app['db'])
        dt = await utils.time.ms_timestamp_to_datetime(
            receipt_data['purchase_date_ms'])
        return await purchases_dao.create(
            platform_type=PlatformType.IOS,
            order_id=receipt_data['transaction_id'],
            product_id=receipt_data['product_id'],
            purchase_at=dt)
