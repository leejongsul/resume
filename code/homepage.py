import logging
import os

import utils.file
import utils.json as json_helper
import utils.multipart as multipart_helper
from dao.descriptions_dao import DescriptionsDao
from dao.downloads_dao import DownloadsDao
from dao.features_dao import FeaturesDao
from dao.images_dao import ImagesDao
from dao.opengraph_dao import OpenGraphDao
from dao.presskits_dao import PressKitsDao
from dao.releases_dao import ReleasesDao
from models.enums import OS, DescriptionType, DownloadType, ImageType


class PresskitService():
    def __init__(self, request, url=None):
        self.request = request
        self.app = request.app
        self.db = self.app['db']
        self.data = None
        self.url = None
        if url is not None:
            self.url = url
        # Dao 초기화
        self.presskits_dao = PressKitsDao(self.db)
        self.releases_dao = ReleasesDao(self.db)
        self.descriptions_dao = DescriptionsDao(self.db)
        self.features_dao = FeaturesDao(self.db)
        self.images_dao = ImagesDao(self.db)
        self.downloads_dao = DownloadsDao(self.db)
        self.opengraph_dao = OpenGraphDao(self.db)

    async def _init_data(self):
        if self.data is not None:
            if 'url' in self.data:
                self.url = self.data['url']

            if 'game_name' in self.data:
                self.game_name = self.data['game_name']
            else:
                self.game_name = None

            if 'images' in self.data and 'screenshots' in self.data['images']:
                self.screenshots = self.data['images']['screenshots']
            else:
                self.screenshots = None
            # Directory
            self.presskit_image_dir = os.path.join(
                self.app['STATIC_ROOT_PATH'],
                self.app['STATIC_IMAGE_BASE_PATH'],
                self.url)
            self.presskit_download_dir = os.path.join(
                self.app['STATIC_ROOT_PATH'],
                self.app['STATIC_ZIP_BASE_PATH'],
                self.url)
            # URL
            self.presskit_download_url_prefix = '{}/{}'.format(
                self.app['STATIC_ZIP_BASE_PATH'],
                self.url)

    async def create_presskit(self):
        try:
            metadata, filedata = await multipart_helper.parse(self.request)
            self.data = await json_helper.dic_to_json(metadata, filedata)
            logging.info(self.data)
            # 값 설정
            await self._init_data()
            # 스크린샷 압축 파일 생성
            url_screenshot_zipfile = await self.generate_sceenshot_zip()
            if url_screenshot_zipfile:
                self.data['download']['screenshot'] = url_screenshot_zipfile
            # PressKit 압축 파일 생성
            url_presskit_zipfile = await self.generate_presskit_zip()
            if url_presskit_zipfile:
                self.data['download']['presskit'] = url_presskit_zipfile
            # DB에 생성
            async with self.db.acquire() as conn:
                trans = await conn.begin()
                try:
                    # PressKits
                    presskit_id = await self.presskits_dao.create(self.data)
                    # Releases
                    await self._create_releases(presskit_id)
                    # Descriptions
                    await self._create_descriptions(presskit_id)
                    # Features
                    await self._create_features(presskit_id)
                    # Images
                    await self._create_images(presskit_id)
                    # Downloads
                    await self._create_downloads(presskit_id)
                    # OpenGraph
                except Exception as e:
                    logging.exception(e)
                    await trans.rollback()
                else:
                    await trans.commit()
        except:
            logging.error('create presskit error. {}'.format(self.url))

    async def get_presskit(self):
        self.url = self.request.match_info['url']
        presskits_dao = PressKitsDao(self.db)
        presskit = await presskits_dao.get_one_all_dict(self.url)
        logging.info("presskit: {}".format(presskit))

        return presskit

    async def list_presskit(self):
        presskits_dao = PressKitsDao(self.db)
        presskits = await presskits_dao.get_list()

        return {
            'presskits': presskits
        }

    async def update_presskit(self):
        self.url = self.request.match_info['url']
        metadata, filedata = await multipart_helper.parse(self.request,
                                                          self.url)
        self.data = await json_helper.dic_to_json(metadata, filedata)
        logging.info("==========================")
        logging.info("modify: {}".format(self.data))
        logging.info("==========================")
        await self._init_data()

        presskit = await self.presskits_dao.get(self.url)
        releases = await self.releases_dao.get_releases(presskit.id)
        descriptions = await self.descriptions_dao.get_descriptions(presskit.id)
        features = await self.features_dao.get_features(presskit.id)
        images = await self.images_dao.get_images(presskit.id)

        async with self.db.acquire() as conn:
            trans = await conn.begin()
            try:
                await self._udpate_presskit(presskit)
                await self._update_releases(presskit.id, releases)
                await self._update_descriptions(presskit.id, descriptions)
                await self._update_features(presskit.id, features)
                await self._update_images(presskit.id, images)
            except Exception as e:
                logging.exception(e)
                await trans.rollback()
                logging.error("rollback presskit update")
            else:
                await trans.commit()
                logging.error("commit presskit update")

    async def delete_presskit(self):
        self.url = self.request.match_info['url']
        # DB에서 삭제
        async with self.db.acquire() as conn:
            trans = await conn.begin()
            try:
                presskit = await self.presskits_dao.get_one_all_dict(self.url)
                self.data = presskit
                await self._init_data()
                logging.info("delete target: {}".format(presskit))
                await self.presskits_dao.delete(presskit['id'])
            except Exception as e:
                await trans.rollback()
                logging.info("presskit(id:{}, game_name:{}) delete failed"
                             .format(presskit['id'], presskit['game_name']))
                logging.exception(e)
            else:
                await trans.commit()
                logging.info("presskit(id:{}, game_name:{}) delete succeed"
                             .format(presskit['id'], presskit['game_name']))
        # 이미지 파일 디렉토리 삭제
        await utils.file.delete(self.presskit_image_dir)
        # 다운로드 압축 파일 디렉토리 삭제
        await utils.file.delete(self.presskit_download_dir)
