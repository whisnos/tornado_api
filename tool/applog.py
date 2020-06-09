import logging
import logging.config
from logging.handlers import RotatingFileHandler
from config import LOGPATH
import re

logging.config.fileConfig(LOGPATH + 'logging.conf', defaults=None)

def get_log(name):
    log_name = '{}'.format(name)
    coin_log = logging.getLogger(log_name)

    log_file_handler = RotatingFileHandler(LOGPATH + 'log/{}.log'.format(log_name), mode='w', maxBytes=0, backupCount=0, encoding='utf-8', delay=False)
    # log_file_handler= TimedRotatingFileHandler(LOGPATH + 'log/{}.log'.format(log_name), when='h', interval=1, backupCount=0)
    # log_file_handler = logging.FileHandler(LOGPATH + 'log/{}.log'.format(log_name),'w', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s [file:%(filename)s line:%(lineno)d %(name)s %(levelname)s]:%(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    # formatter = logging.Formatter('%(asctime)s [file:%(filename)s %(name)s %(levelname)s]:%(message)s',datefmt='%Y-%m-%d %H:%M:%S')

    log_file_handler.setFormatter(formatter)
    coin_log.addHandler(log_file_handler)
    return coin_log
    # self.coin_log.debug('init finish, balance:{balance},payin:{payin}'.format(
    #     balance=self.balance, payin=self.payin))


if __name__ == '__main__':
    l = get_log('tool')
    l.debug('hello tool')
    l.info('hello tool')
    l.warning('hello tool')
    l.error('hello tool')