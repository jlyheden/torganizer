__author__ = 'johan'

import logging
import argparse
from torganizer.setup import get_config, setup

logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser(description='Torrent Organizer script')
parser.add_argument('--config', dest='config_path', action='store', type=str, help='Path to torganizer config yaml')
parser.add_argument('--src', dest='src', action='store', type=str, help='Source folder to organize')
args = parser.parse_args()

config = get_config(args.config_path)
handler = setup(config, args.src)
handler.execute()