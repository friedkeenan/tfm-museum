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
EXTERNAL_DIR = "external"

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

    # TODO: TaskGroup in Python 3.11.
    tasks = []

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

                tasks.append(download(archive_dir, download_url))

            else:
                for descriptor in background_images.split(";"):
                    image_path = descriptor.split(",", 1)[0]

                    tasks.append(download(archive_dir, TRANSFORMICE_IMAGE_PARENT_URL + image_path))

        foreground_images = settings.get("d")
        if foreground_images is not None:
            for descriptor in foreground_images.split(";"):
                image_path = descriptor.split(",", 1)[0]

                tasks.append(download(archive_dir, TRANSFORMICE_IMAGE_PARENT_URL + image_path))

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

            tasks.append(download(archive_dir, download_url))

    archived_xml_path = Path(archive_dir, MAPS_SUBDIRECTORY, xml_path.relative_to(data_dir))
    await aiofiles.os.makedirs(archived_xml_path.parent, exist_ok=True)

    async with aiofiles.open(archived_xml_path, "w") as f:
        await asyncio.gather(f.write(xml_data), *tasks)

async def archive_misc_urls(data_dir, archive_dir, urls_path):
    # TODO: TaskGroup in Python 3.11.
    tasks = []

    async with aiofiles.open(urls_path) as f:
        async for url in f:
            url = url.strip()

            if len(url) <= 0:
                continue

            tasks.append(download(archive_dir, url))

    await asyncio.gather(*tasks)

async def make_archive(data_dir, archive_dir):
    if await aiofiles.os.path.exists(archive_dir):
        raise ValueError(f"Specified archive directory '{archive_dir}' already exists")

    if not await aiofiles.os.path.exists(data_dir):
        raise ValueError(f"Specified data directory '{data_dir}' does not exist")

    # TODO: TaskGroup in Python 3.11.
    tasks = []

    tasks.append(download(archive_dir, "http://www.transformice.com/Transformice.swf"))
    tasks.append(download(archive_dir, "http://www.transformice.com/TransformiceChargeur.swf"))

    for xml_path in data_dir.glob(XML_PATH_GLOB):
        tasks.append(archive_external_map_data(data_dir, archive_dir, xml_path))

    for urls_path in data_dir.glob(MISC_URLS_PATH_GLOB):
        tasks.append(archive_misc_urls(data_dir, archive_dir, urls_path))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("data_dir", type=Path)
    parser.add_argument("archive_dir", type=Path)

    args = parser.parse_args()

    asyncio.run(make_archive(args.data_dir, args.archive_dir))
