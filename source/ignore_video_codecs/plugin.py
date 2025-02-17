#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    unmanic-plugins.plugin.py
    Written by:               Josh.5 <jsunnex@gmail.com>
    Date:                     11 Aug 2021, (7:09 AM)
    Copyright:
        Copyright (C) 2021 Josh Sunnex
        This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
        Public License as published by the Free Software Foundation, version 3.
        This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
        implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
        for more details.
        You should have received a copy of the GNU General Public License along with this program.
        If not, see <https://www.gnu.org/licenses/>.
"""
import logging

from unmanic.libs.unplugins.settings import PluginSettings

from ignore_video_codecs.lib.ffmpeg import StreamMapper, Probe

# Configure plugin logger
logger = logging.getLogger("Unmanic.Plugin.ignore_video_codecs")


class Settings(PluginSettings):
    settings = {
        "excluded_codecs": "h264,h265"
    }

    def __init__(self):
        self.form_settings = {
            "excluded_codecs": self.__set_exclude_codecs_form_settings(),
        }

    def __set_exclude_codecs_form_settings(self):
        values = {
            "label":      "Video codecs to skip",
            "input_type": "textarea",
        }
        return values

class PluginStreamMapper(StreamMapper):
    image_video_codecs = [
        'alias_pix',
        'apng',
        'brender_pix',
        'dds',
        'dpx',
        'exr',
        'fits',
        'gif',
        'mjpeg',
        'mjpegb',
        'pam',
        'pbm',
        'pcx',
        'pfm',
        'pgm',
        'pgmyuv',
        'pgx',
        'photocd',
        'pictor',
        'pixlet',
        'png',
        'ppm',
        'ptx',
        'sgi',
        'sunrast',
        'tiff',
        'vc1image',
        'wmv3image',
        'xbm',
        'xface',
        'xpm',
        'xwd',
    ]

    def __init__(self, excluded_codecs: list):
        super(PluginStreamMapper, self).__init__(logger, ['video'])
        self.excluded_codecs = excluded_codecs

    def test_stream_needs_processing(self, stream_info: dict):
        if stream_info.get('codec_name').lower() in self.image_video_codecs:
            return False
        elif stream_info.get('codec_name').lower() in self.excluded_codecs:
            return False
        return True

    def custom_stream_mapping(self, stream_info: dict, stream_id: int):
        # Skip mapping
        return {
            'stream_mapping':  [],
            'stream_encoding': [],
        }


def on_library_management_file_test(data):
    """
    Runner function - enables additional actions during the library management file tests.
    The 'data' object argument includes:
        path                            - String containing the full path to the file being tested.
        issues                          - List of currently found issues for not processing the file.
        add_file_to_pending_tasks       - Boolean, is the file currently marked to be added to the queue for processing.
    :param data:
    :return:
    """
    # Get the path to the file
    abspath = data.get('path')

    # Get file probe
    probe = Probe(logger, allowed_mimetypes=['video'])
    if not probe.file(abspath):
        # File probe failed, skip the rest of this test
        return data

    # Get settings
    settings = Settings()
    excluded_codecs = [x.strip().lower() for x in settings.get_setting("excluded_codecs").split(',')]

    # Get stream mapper
    mapper = PluginStreamMapper(excluded_codecs)
    mapper.set_probe(probe)

    if mapper.streams_need_processing():
        # Don't ignore this file
        logger.debug("File '{}' does not contain streams with an ignored codec.".format(abspath))
    else:
        # Ignore this file
        data['add_file_to_pending_tasks'] = False
        logger.debug("File '{}' contains an ignored video codec.".format(abspath))

    return data
