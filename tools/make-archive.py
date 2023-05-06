#!/usr/bin/env python3

import asyncio
import aiofiles
import aiofiles.os
import aiohttp

import re

from pathlib   import Path
from xml.etree import ElementTree

XML_PATH_GLOB       = "**/*.xml"
MISC_URLS_PATH_GLOB = "**/misc-urls.txt"

MAPS_SUBDIRECTORY = "maps"
EXTERNAL_DIR      = "external"

TRANSFORMICE_SWF_URL          = "http://www.transformice.com/Transformice.swf"
TRANSFORMICE_CHARGEUR_SWF_URL = "http://www.transformice.com/TransformiceChargeur.swf"

TRANSFORMICE_IMAGE_PARENT_URL = "http://www.transformice.com/images/"

ATELIER_IMAGE_PATTERN    = re.compile(r"^[a-z0-9]+\.[a-z]+$", flags=re.IGNORECASE)
ATELIER_IMAGE_PARENT_URL = "http://images.atelier801.com/"

async def download(archive_dir, url):
    download_path = Path(archive_dir, EXTERNAL_DIR, url.split("://", 1)[1])

    if await aiofiles.os.path.exists(download_path):
        # TODO: Make sure this is actually an indicator
        # that the image is being/already is downloaded.

        return

    await aiofiles.os.makedirs(download_path.parent, exist_ok=True)

    async with aiofiles.open(download_path, "wb") as f:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                await f.write(await response.read())

async def archive_external_map_data(data_dir, archive_dir, xml_path):
    async with aiofiles.open(xml_path) as f:
        xml_data = await f.read()

    xml = ElementTree.fromstring(xml_data)

    async with asyncio.TaskGroup() as tg:
        async def copy_xml():
            archived_xml_path = Path(archive_dir, MAPS_SUBDIRECTORY, xml_path.relative_to(data_dir))
            await aiofiles.os.makedirs(archived_xml_path.parent, exist_ok=True)

            async with aiofiles.open(archived_xml_path, "w") as f:
                await f.write(xml_data)

        tg.create_task(copy_xml())

        # NOTE: The XML parsing here as the same behavior as the client.

        if len(xml) > 0:
            settings = xml[0]

            background_images = settings.get("D")
            if background_images is not None:
                if background_images.startswith("#"):
                    image_path = background_images[1:]

                    download_url = None
                    if "://" in image_path:
                        download_url = image_path
                    else:
                        download_url = TRANSFORMICE_IMAGE_PARENT_URL + image_path

                    tg.create_task(
                        download(archive_dir, download_url)
                    )

                else:
                    for descriptor in background_images.split(";"):
                        image_path = descriptor.split(",", 1)[0]

                        tg.create_task(
                            download(archive_dir, TRANSFORMICE_IMAGE_PARENT_URL + image_path)
                        )

            foreground_images = settings.get("d")
            if foreground_images is not None:
                for descriptor in foreground_images.split(";"):
                    image_path = descriptor.split(",", 1)[0]

                    tg.create_task(
                        download(archive_dir, TRANSFORMICE_IMAGE_PARENT_URL + image_path)
                    )

        if len(xml) > 1:
            zone    = xml[1]
            grounds = zone[0]

            for ground in grounds:
                image_descriptor = ground.get("i")
                if image_descriptor is None:
                    continue

                descriptors = image_descriptor.split(",")
                if len(descriptors) < 3:
                    continue

                image_path = descriptors[2]

                download_url = None
                if ATELIER_IMAGE_PATTERN.match(image_path) is not None:
                    download_url = ATELIER_IMAGE_PARENT_URL + image_path

                elif "://" not in image_path:
                    download_url = TRANSFORMICE_IMAGE_PARENT_URL + image_path

                else:
                    download_url = image_path

                tg.create_task(
                    download(archive_dir, download_url)
                )

async def archive_misc_urls(data_dir, archive_dir, urls_path):
    async with asyncio.TaskGroup() as tg:
        async with aiofiles.open(urls_path) as f:
            async for url in f:
                url = url.strip()

                # We ignore comments.
                #
                # NOTE: URLs can have '#' within them,
                # but then they would indicate a 'fragment
                # identifier', which does not change the
                # content of the webpage.
                url = url.split("#", 1)[0]

                if len(url) <= 0:
                    continue

                tg.create_task(
                    download(archive_dir, url)
                )

async def make_archive(data_dir, archive_dir):
    if await aiofiles.os.path.exists(archive_dir):
        raise ValueError(f"Specified archive directory '{archive_dir}' already exists")

    if not await aiofiles.os.path.exists(data_dir):
        raise ValueError(f"Specified data directory '{data_dir}' does not exist")

    async with asyncio.TaskGroup() as tg:
        tg.create_task(
            download(archive_dir, TRANSFORMICE_SWF_URL)
        )

        tg.create_task(
            download(archive_dir, TRANSFORMICE_CHARGEUR_SWF_URL)
        )

        for xml_path in data_dir.glob(XML_PATH_GLOB):
            tg.create_task(
                archive_external_map_data(data_dir, archive_dir, xml_path)
            )

        for urls_path in data_dir.glob(MISC_URLS_PATH_GLOB):
            tg.create_task(
                archive_misc_urls(data_dir, archive_dir, urls_path)
            )

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("data_dir", type=Path)
    parser.add_argument("archive_dir", type=Path)

    args = parser.parse_args()

    asyncio.run(make_archive(args.data_dir, args.archive_dir))
